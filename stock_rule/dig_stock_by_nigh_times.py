#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' low 9 module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from init_sql import *
from util.multi_processes import *

class Dig_Stock_By_Nigh_Times(Process_Job, Multi_Processes):

    ############################################# 九转选股之日线低9  #######################################################
    def dig_stock_by_nigh_times(self, records, times=9, continuous_ref_times=4):
        queue_close = []
        continuous_time = 0

        for index, row in enumerate(records):
            code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
            ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[
                                                                                                             :27]

            queue_close.append(float(close))
            if (index < (continuous_ref_times - 1)):
                # 交易日小于，等于4 只记录收盘价
                continue

            ref_continuous_time = True
            # for last_close in queue_close:
            last_close = queue_close[0]
            if (close > last_close):
                ref_continuous_time = False

            if (True == ref_continuous_time):
                continuous_time = continuous_time + 1
            elif (False == ref_continuous_time):
                continuous_time = 0

            # 已找到符合条件个股
            if (continuous_time >= times):
                #if (yesterday() < date):
                print("低九", date, get_stock_basic(code))
                continuous_time = 0
            queue_close.pop(0)

    def process(self, start_date, end_date, from_table, to_table, stock_index, index, list_len):
        # 打印进度 时间 ID
        # print("processed: %s%%,  Id:%s,  Time:%s" % (int((index / list_len) * 100), stock_index, (str(datetime.datetime.now()))))

        # 取原始数据
        records = get_stock_raw_data_from_mysql(stock_index, start_date, end_date, from_table)
        if (len(records) > 0):
            # 挖掘九转出低九
            self.dig_stock_by_nigh_times(records, 9)

    def __init__(self, start_date, end_date, from_table, to_table):
        # 初始化本策略参数
        super().__init__(start_date, end_date, from_table, to_table)
        return