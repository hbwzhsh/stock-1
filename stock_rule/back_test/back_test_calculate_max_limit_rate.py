#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' back test max lose module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from util.common import *
from util.multi_processes import *

class Back_Test_Calculat_Max_Limit_Rate(Process_Job, Multi_Processes):
    ########################################################################################################################
    #########################################         回测涨停率        ####################################################
    ########################################################################################################################
    def calculat_stock_max_limit(self,records):
        limit_up_times = 0
        limit_down_times = 0
        last_close = 0
        launch_date = '1971-1-1'
        for index, row in enumerate(records):
            code, date, open, high, low, close, volume, turnover = row[:8]
            if (index < 1):
                last_close = close
                launch_date = date
                continue
            if (((close - last_close) / last_close) > 0.091):
                limit_up_times = limit_up_times + 1
            elif (((close - last_close) / last_close) < -0.091):
                limit_down_times = limit_down_times + 1
            last_close = close

        return index, launch_date, limit_up_times, my_round(limit_up_times / index), limit_down_times, my_round(
            limit_down_times / index)

    def process(self, start_date, end_date, from_table, to_table, stock_index, index, list_len):
        super().process_calculat_stock_rate(self.calculat_stock_max_limit, 'max limit', start_date, end_date, from_table,
                           to_table, stock_index, index, list_len)

    def __init__(self, start_date, end_date, from_table, to_table):
        # 初始化本策略参数
        super().__init__(start_date, end_date, from_table, to_table)


