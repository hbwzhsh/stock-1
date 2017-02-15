#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' back test max lose module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from util.common import *
from util.multi_processes import *

class Back_Test_Calculat_Stock_Max_Lose(Process_Job, Multi_Processes):
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
        super().process_calculat_stock_rate(self.calculat_stock_max_lose, 'max lost', start_date, end_date, from_table,
                           to_table, stock_index, index, list_len)

    def __init__(self, start_date, end_date, from_table, to_table):
        # 初始化本策略参数
        super().__init__(start_date, end_date, from_table, to_table)

