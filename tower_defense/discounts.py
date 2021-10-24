import pytz
import datetime

from typing import *


def getDiscount() -> List[Union[str, int]]:
    now = datetime.datetime.now(tz=pytz.timezone('Singapore'))

    for date in discountDates:
        if date[0] == [now.year, now.month, now.day]:
            return date[1]


discountDates = [
    [[2021, 10, 24], ['Programmers\' Day', 25]],
    [[2021, 10, 31], ['Spooky Halloween', 15]],
    [[2021, 11, 20], ['School Holidays', 25]],
    [[2021, 12, 24], ['Christmas Eve', 20]],
    [[2021, 12, 25], ['Christmas Day', 40]]
]
