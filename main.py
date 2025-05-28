
import logging
from math import sqrt
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from fastapi import FastAPI
from finsim.estimate.fit import fit_BlackScholesMerton_model, fit_multivariate_BlackScholesMerton_model
from finsim.estimate.risk import estimate_downside_risk, estimate_upside_risk, estimate_beta
from lppl.fit import LPPLModel
from dotenv import load_dotenv

from helpers.data import waiting_get_yahoofinance_data
from apischemas.schemas import SymbolEstimationResult, SymbolsCorrelationResult, LPPLCrashModelResult, FittedLPPLModelParameters


# load additional environment variables
load_dotenv()


# starting FastAPI app
app = FastAPI()


# root, health check
@app.get("/")
async def root():
    return {"message": "API health check successful"}


@app.get("/v0/estimate-symbol-info", response_model=SymbolEstimationResult)
def estimate_symbol_info(
        symbol: str,
        startdate: str,
        enddate: str,
        index: str='^GSPC'    # i.e., S&P 500 index as the base for calculating beta
):
    # getting stock data
    symdf = waiting_get_yahoofinance_data(symbol, startdate, enddate)
    print("Number of lines: {}".format(len(symdf)))

    # getting index
    indexdf = waiting_get_yahoofinance_data(index, startdate, enddate)

    # estimation
    isrownull = symdf['Close'].isnull()
    r, sigma = fit_BlackScholesMerton_model(
        symdf.loc[~isrownull, 'TimeStamp'].to_numpy(),
        symdf.loc[~isrownull, 'Close'].to_numpy()
    )
    downside_risk = estimate_downside_risk(
        symdf.loc[~isrownull, 'TimeStamp'].to_numpy(),
        symdf.loc[~isrownull, 'Close'].to_numpy(),
        0.0
    )
    upside_risk = estimate_upside_risk(
        symdf.loc[~isrownull, 'TimeStamp'].to_numpy(),
        symdf.loc[~isrownull, 'Close'].to_numpy(),
        0.0
    )
    try:
        mgdf = indexdf[['TimeStamp', 'Close']].merge(symdf[['TimeStamp', 'Close']], on='TimeStamp', how='left')
        mgdf = mgdf.loc[~pd.isna(mgdf['Close_x']) & ~pd.isna(mgdf['Close_y']), :]
        beta = estimate_beta(
            mgdf['TimeStamp'].to_numpy(),
            mgdf['Close_y'].to_numpy(),
            mgdf['Close_x'].to_numpy()
        )
    except:
        logging.warning('Index {} failed to be integrated.'.format(index))
        beta = None

    return SymbolEstimationResult(
        symbol=symbol,
        r=r,
        volatility=sigma,
        downside_risk=downside_risk,
        upside_risk=upside_risk,
        beta=beta if beta is not None else None,
        data_startdate=symdf['TimeStamp'][0].date(),
        data_enddate=symdf['TimeStamp'][len(symdf) - 1].date(),
        nbrecords=len(symdf.loc[~isrownull, :])
    )


@app.get("/v0/estimate-symbols-correlation", response_model=SymbolsCorrelationResult)
def estimate_symbols_correlation(
        symbol1: str,
        symbol2: str,
        startdate: str,
        enddate: str
):
    # get symbols' prices
    sym1df = waiting_get_yahoofinance_data(symbol1, startdate, enddate)
    sym2df = waiting_get_yahoofinance_data(symbol2, startdate, enddate)
    combined_df = sym1df[['TimeStamp', 'Close']].rename(columns={'Close': 'Close1'}). \
        merge(
        sym2df[['TimeStamp', 'Close']].rename(columns={'Close': 'Close2'}),
        on='TimeStamp', how='inner'
    )

    # computation
    rarray, covmat = fit_multivariate_BlackScholesMerton_model(
        combined_df['TimeStamp'].to_numpy(),
        np.array([
            combined_df['Close1'].to_numpy(),
            combined_df['Close2'].to_numpy()
        ])
    )

    return SymbolsCorrelationResult(
        symbol1=symbol1,
        symbol2=symbol2,
        r1=rarray[0],
        r2=rarray[1],
        std1=sqrt(covmat[0, 0]),
        std2=sqrt(covmat[1, 1]),
        covariance=covmat[1, 0],
        correlation=covmat[1, 0] / sqrt(covmat[0, 0] * covmat[1, 1]),
        startdate=startdate,
        enddate=enddate
    )

@app.get("/v0/predict-crash", response_model=LPPLCrashModelResult)
def predict_crash(
        symbol: str="^GSPC",   # default to be S&P 500
        startdate: str=None,
        enddate: str=None
):
    if startdate is None:
        startdate = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    if enddate is None:
        enddate = datetime.today().strftime('%Y-%m-%d')

    # get symbols
    symdf = waiting_get_yahoofinance_data(symbol, startdate, enddate)

    # fitting
    fitted_lppl_model = LPPLModel()
    fitted_lppl_model.tcgap = 60 * 60 * 24
    fitted_lppl_model.fit(symdf['TimeStamp'].map(lambda ts: ts.timestamp()), symdf['Close'])

    # gathering output
    model_parameters = fitted_lppl_model.dump_model_parameters()
    return LPPLCrashModelResult(
        symbol=symbol,
        startdate=startdate,
        enddate=enddate,
        estimated_crash_date=pd.Timestamp.fromtimestamp(model_parameters['tc']).strftime('%Y-%m-%d'),
        estimated_crash_time=str(pd.Timestamp.fromtimestamp(model_parameters['tc'])),
        model_parameters=FittedLPPLModelParameters(**model_parameters)
    )
