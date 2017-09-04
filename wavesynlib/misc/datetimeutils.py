# -*- coding: utf-8 -*-
"""
Created on Sun Sep  3 19:21:42 2017

@author: Feng-cong Li
"""
from datetime import timedelta



class WeekNumberTool:
    def __init__(self, date, weeknum):
        self.__first_monday = \
            date - timedelta(weeks=weeknum-1, days=date.weekday())
        
        
        
    def get_date(self, weeknum, weekday):
        return self.__first_monday + timedelta(weeks=weeknum-1, days=weekday)
    
    
    @property
    def first_monday(self):
        return self.__first_monday
        