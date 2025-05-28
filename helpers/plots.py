
from datetime import datetime


def get_optimal_daybreaks(startdate: str, enddate: str) -> str:
    timediff = datetime.strptime(enddate, '%Y-%m-%d') - datetime.strptime(startdate, '%Y-%m-%d')
    nbdaysdiff = timediff.days
    if nbdaysdiff > 730:
        return '1 year'
    elif nbdaysdiff > 365:
        return '3 months'
    elif nbdaysdiff > 30:
        return '1 month'
    else:
        return '1 day'
