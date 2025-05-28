
from datetime import date

from pydantic import BaseModel, ConfigDict


class SymbolEstimationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    symbol: str
    r: float
    volatility: float
    downside_risk: float
    upside_risk: float
    beta: float
    data_startdate: date
    data_enddate: date
    nbrecords: int


class SymbolsCorrelationResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    symbol1: str
    symbol2: str
    r1: float
    r2: float
    std1: float
    std2: float
    covariance: float
    correlation: float
    startdate: date
    enddate: date
