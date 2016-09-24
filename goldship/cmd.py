import sys
import datetime
import calendar
from goldship import scraper


def race_result():
    year, month, day = sys.argv[1:4]
    scraper.race_result(year, month, day)


def race_result_year():
    year = int(sys.argv[1])
    month_days = [[i + 1 for i in range(calendar.monthrange(year, month)[1])]
                  for month in range(11, 13)]
    for month, days in enumerate(month_days, start=11):
        [scraper.race_result(year, month, day) for day in days]
