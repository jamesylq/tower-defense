import pytz
import datetime

from typing import *


def getDiscount() -> List[Union[str, int]]:
    now = datetime.datetime.now(tz=pytz.timezone('Singapore'))

    for date in discountDates:
        if date[0] == [now.year, now.month, now.day]:
            return date[1]


discountDates = []
