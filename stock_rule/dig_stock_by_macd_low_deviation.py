#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' macd low deviation module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from init_sql import *
from util.multi_processes import *

class Dig_Stock_By_Macd_Low_Deviation(Process_Job, Multi_Processes):

    __slots__ = ('__start_date', '__end_date','__from_table', '__to_table')  # 用tuple定义允许绑定的属性名称

    ############################################# 计算MACD日线底背离 #######################################################
    def dig_stock_macd_deviation(self, records):
        first_golden = 0
        first_low_close = 0.0
        first_golden_date = '1971-1-1'
        first_low_diff = 0.0
        first_red_bar_num = 0
        second_low_diff = 0.0
        second_low_close = 0.0
        second_green_bar_num = 0
        first_dead = 0
        first_daed_date = '1971-1-1'

        for row in records:
            code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, ma8, ma10, ma13, ma20, \
                ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[:27]
            if (first_golden == 0):  # 记录第一次金叉前的最小diff
                if (first_low_diff > diff):
                    first_low_diff = diff
                    first_low_close = close
            elif (first_golden == 1):
                if (diff > 0):  # 第一次金叉后，diff穿0轴，则视为金叉无效，所有条件reset
                    first_golden = 0
                    first_golden_date = '1971-1-1'
                    first_low_diff = 0
                    first_low_close = 0
                    first_red_bar_num = 0
                    second_low_diff = 0
                    second_low_close = '1971-1-1'
                    first_dead = 0
                    second_green_bar_num = 0
                # 记录第二次金叉前的最小diff
                if (second_low_diff > diff):
                    second_low_diff = diff
                    second_low_close = close

            # 第一次金叉后的red bar 连续大于0的数目
            if (bar > 0 and first_golden == 1):
                first_red_bar_num = first_red_bar_num + 1

            # diff小于0后第一次金叉后的死叉后 bar连续小于0的数目
            if (bar < 0 and first_dead == 1):
                second_green_bar_num = second_green_bar_num + 1

            # 金叉且 diff 小于0
            if (diff > dea) and diff < 0:
                # 底背离成立
                if ((first_golden == 1) and (first_dead == 1) and (
                    second_low_close < first_low_close) and second_low_diff > first_low_diff and second_green_bar_num >= 2):
                    #print("底背离:", code, get_stock_detail(code), first_golden_date, first_low_close, second_low_close, first_daed_date, date, close)
                    return
                # diff<0后第一次金叉
                if (first_golden == 0):
                    first_golden = 1
                    first_golden_date = date
            # diff小于0后第一次金叉后的死叉
            elif (diff < dea) and diff < 0:
                if ((first_golden == 1) and (first_dead == 0) and first_red_bar_num >= 2):
                    first_dead = 1
                    first_daed_date = date
                # 如果金叉后又要死叉时，绿柱数目小于2，则视为本次背离已失效，所有条件reset
                elif ((first_golden == 1) and (first_dead == 0) and first_red_bar_num < 2):
                    first_golden = 0
                    first_golden_date = '1971-1-1'
                    first_low_diff = 0
                    first_low_close = 0
                    first_red_bar_num = 0
                    second_low_diff = 0
                    second_low_close = '1971-1-1'
                    first_dead = 0
                    second_green_bar_num = 0

        # 底背离尚未形成 已钝化
        if ((first_golden == 1) and (first_dead == 1) and (
                    second_low_close < first_low_close) and second_low_diff > first_low_diff and second_green_bar_num > 2):
            print("钝化:", code, get_stock_detail(code), first_golden_date, first_low_close, second_low_close,
                  first_daed_date, date, close)

        return

    def process(self, start_date, end_date, from_table, to_table, stock_index, index, list_len):
        # 打印进度 时间 ID
        # print("processed: %s%%,  Id:%s,  Time:%s" % (int((index / list_len) * 100), stock_index, (str(datetime.datetime.now()))))

        # 取原始数据
        records = get_stock_raw_data_from_mysql(stock_index, start_date, end_date, from_table)
        if (len(records) > 0):
            # 挖掘MACD底背离
            self.dig_stock_macd_deviation(records)

    def __init__(self, start_date, end_date, from_table, to_table):
        # 初始化本策略参数
        super().__init__(start_date, end_date, from_table, to_table)
