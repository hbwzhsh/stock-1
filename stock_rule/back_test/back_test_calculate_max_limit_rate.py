#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' back test max lose module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from init_sql import *

class Back_Test_Calculat_Max_Limit_Rate(Process_Job):
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
        self.process_calculat_stock_rate(self.calculat_stock_max_limit, 'max limit', start_date, end_date, from_table,
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

