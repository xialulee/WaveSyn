from datetime import timedelta


class WeekNumberTool:
    def __init__(self, date, weeknum):
        weeknum -= 1
        self.__first_monday = date - timedelta(weeks=weeknum, days=date.weekday())

    def get_date(self, weeknum, weekday):
        weeknum -= 1
        return self.first_monday + timedelta(weeks=weeknum, days=weekday)

    def get_weeknum(self, date):
        delta = (date - self.first_monday).days // 7
        return delta + 1

    @property
    def first_monday(self):
        return self.__first_monday