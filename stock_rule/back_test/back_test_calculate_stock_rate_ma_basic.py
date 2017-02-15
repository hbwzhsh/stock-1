#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' back test max lose module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from util.common import *
from util.multi_processes import *

class Back_Test_Calculate_Stock_Rate_MA_Basic(Process_Job, Multi_Processes):
    ####################################### 收盘价大于MA 买入，小于MA卖出 #################################################
    def calculate_stock_rate_ma_basic(self, records):
        buy_stock_list = []  # 买入列表
        sell_stock_list = []  # 卖出列表
        is_buy = 0
        buy_ma = self.__buy_ma
        sell_ma = self.__sell_ma

        for row in records:
            code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
            ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120 = row[:22]
            m_ma_buy = locals()[u'ma%d' % buy_ma]
            m_ma_sell = locals()[u'ma%d' % sell_ma]

            if (not ((open == close) and (high == low) and (open == high))):
                # 价格都相等时，什么都不做
                # print("All Equal open=%s close=%s high=%s low=%s" %(open, close, high, low))
                # else:
                if (float(close) > m_ma_buy) and (float(volume) > 10000):
                    if is_buy == 0:
                        is_buy = 1
                        buy_stock_list.append((code, date, open, high, low, close, volume, m_ma_buy))
                elif (float(close) < m_ma_sell) and (float(volume) > 10000):
                    if is_buy == 1:
                        is_buy = 0
                        sell_stock_list.append((code, date, open, high, low, close, volume, m_ma_sell))
        return buy_stock_list, sell_stock_list

    def process(self, start_date, end_date, from_table, to_table, stock_index, index, list_len):
        super().process_back_test(self.calculate_stock_rate_ma_basic, 'MA%s' %self.__buy_ma, start_date, end_date,
                               from_table, to_table, stock_index, index, list_len)


    def __init__(self, start_date, end_date, from_table, to_table, buy_ma, sell_ma):
        # 初始化本策略参数
        super().__init__(start_date, end_date, from_table, to_table)
        self.__buy_ma     = buy_ma       #大于buy_ma买入
        self.__sell_ma    = sell_ma      #小于buy_ma卖出
        return