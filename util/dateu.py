# -*- coding:utf-8 -*-

import datetime


 
def today():
    day = datetime.date.today()
    return day.strftime("%Y-%m-%d")

def yesterday():
    day = datetime.date.today() - datetime.timedelta(days=1)
    return day #.strftime("%Y-%m-%d")
