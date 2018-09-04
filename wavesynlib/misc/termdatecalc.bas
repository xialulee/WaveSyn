Attribute VB_Name = "Module1"
Function calc_term_date(ByVal origin As Date, ByVal week_num As Integer, ByVal week_day As Integer) As Date
'Calc the date of a term based on given week number and week day.
'
'origin: the date of the monday on the first week.
'week_num: the week number.
'week_day: the weekday; 1 for Monday and 7 for Sunday.
'
'return: the corresponding date.

    wd = Weekday(origin, vbMonday)
    origin = DateAdd("d", -(wd - 1), origin)
    d1 = DateAdd("ww", week_num - 1, origin)
    d2 = DateAdd("d", week_day - 1, d1)
    calc_term_date = d2
End Function
