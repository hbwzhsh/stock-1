#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' back test max lose module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from init_sql import *

class Back_Test_Calculat_Stock_Max_Lose(Process_Job):
    ###################################### 计算一段时间内最大跌幅  ################################################
    def calculat_stock_max_lose(self, records):
        limit_up_times = 0
        limit_down_times = 0
        max_close = 0.0
        max_date = '1971-1-1'
        for index, row in enumerate(records):
            code, date, open, high, low, close, volume, turnover = row[:8]
            if (index < 1):
                max_close = close
                max_date = date
                continue
            if (close > max_close):
                max_close = close
                max_date = date

        return index, max_date, 0, max_close, 0, my_round((max_close - close) / max_close)


    def process(self, start_date, end_date, from_table, to_table, stock_index, index, list_len):
        self.process_calculat_stock_rate(self.calculat_stock_max_lose, 'max lost', start_date, end_date, from_table,
                           to_table, stock_index, index, list_len)

    def __init__(self, start_date, end_date, from_table, to_table):
        # 初始化本策略参数
        self.__start_date = start_date   #开始时间
        self.__end_date   = end_date     #结束时间
        self.__from_table = from_table   # 数据源
        self.__to_table   = to_table     # 目标表
        return

    def get_list(self):
        return get_stock_index_list_from_mysql(self.__from_table)

    def get_args(self):
        return self.__start_date, self.__end_date, self.__from_table, self.__to_table

