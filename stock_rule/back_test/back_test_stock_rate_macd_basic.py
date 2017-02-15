#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' back test max lose module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from util.common import *

class Back_Test_Stock_Rate_Macd_Basic(Process_Job):
    ####################################### MACD金叉买入，MACD死叉卖出 #################################################
    def calculate_stock_rate_macd_basic(self,records):
        buy_stock_list = []  # 买入列表
        sell_stock_list = []  # 卖出列表
        is_buy = 0

        for row in records:
            code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
            ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[:27]

            if (not ((open == close) and (high == low) and (open == high))):
                # 价格都相等时，什么都不做
                # print("All Equal open=%s close=%s high=%s low=%s" %(open, close, high, low))
                # else:
                if (float(diff) > float(dea)) and (float(volume) > 10000):  # and(float(diff)<0):
                    if is_buy == 0:
                        is_buy = 1
                        buy_stock_list.append((code, date, open, high, low, close, volume))
                        # print(date)
                elif (float(diff) < float(dea)) and (float(volume) > 10000):
                    if is_buy == 1:
                        is_buy = 0
                        sell_stock_list.append((code, date, open, high, low, close, volume))

        return buy_stock_list, sell_stock_list


    def process(self, start_date, end_date, from_table, to_table, stock_index, index, list_len):

        self.process_back_test(self.calculate_stock_rate_macd_basic, 'macd basic', start_date, end_date,
                               from_table, to_table, stock_index, index, list_len)



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

