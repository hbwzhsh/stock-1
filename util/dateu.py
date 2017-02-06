#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' a date module '

__author__ = 'Yuechen Yang'

import datetime


 
def today():
    day = datetime.date.today()
    return day.strftime("%Y-%m-%d")


def yesterday():
    day = datetime.date.today() - datetime.timedelta(days=1)
    return day #.strftime("%Y-%m-%d")

def log_date_time(func):
    def wrapper(*args, **kw):
        print('@%s call %s():' %(str(datetime.datetime.now()), func.__name__))
        return func(*args, **kw)
    return wrapper