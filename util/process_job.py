#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' multi job module '

__author__ = 'Yuechen Yang'

import multiprocessing
from util import vars as vs
from util.operate_mysql import *

class Process_Job(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def get_list(self):
        pass

    def get_args(self):
        pass

    def process(self):
        pass

    ###################################### 回测数据 ################################################
    def process_calculat_stock_rate(self, function, key_condition, start_date, end_date, from_table, to_table, stock_index, index, list_len):
        records = get_stock_raw_data_from_mysql(stock_index, start_date, end_date, from_table)
        if (len(records) <= 0):
            return
        # 使用策略后 获得买入卖出时间 价格列表
        deal_days, launch_date, limit_up_times, limit_up_times_rate, limit_down_times, limit_down_times_rate = function(
            records)

        # 插入数据库
        operatMySQl = OperateMySQL()
        sqli = "insert into {0} values ('{1}','{2}',{3},\"{4}\",{5},{6},{7},{8});"
        sqlm = sqli.format(to_table, stock_index,key_condition, deal_days, launch_date, limit_up_times, limit_up_times_rate,
                           limit_down_times, limit_down_times_rate)
        try:
            operatMySQl.execute(sqlm)
            # print(sqlm)
        except:
            print("Insert Error", sqlm)

        operatMySQl.commit()
        return

    ###################################### 回测数据 ################################################
    def process_back_test(self, function, key_condition, start_date, end_date, from_table, to_table, stock_index, index, list_len):

        buy_stock_list = []  # 买入列表
        sell_stock_list = []  # 卖出列表
        profit_rate = 1.0
        max_single_win_rate = 1.0  # 单次最大收益率
        max_single_lose_rate = 1.0  # 单次最大亏损率
        win_times = 0  # 盈利次数
        lose_times = 0  # 亏损次数

        records = get_stock_raw_data_from_mysql(stock_index, start_date, end_date, from_table)
        if (len(records) <= 0):
            return

        # 使用策略后 获得买入卖出时间 价格列表
        buy_stock_list, sell_stock_list = function(records)

        buy_count = len(buy_stock_list)  # 买入次数
        sell_count = len(sell_stock_list)  # 卖出次数

        max_rate_buy_date = '1971-1-1'  # 单次最大盈利买入时间
        max_rate_sell_date = '1971-1-1'  # 单次最大盈利卖出时间

        max_lose_rate_buy_date = '1971-1-1'  # 单次最大盈利买入时间
        max_lose_rate_sell_date = '1971-1-1'  # 单次最大盈利卖出时间

        for (buy_stock, sell_stock) in zip(buy_stock_list, sell_stock_list):
            sell_price = round(float(sell_stock[5]), 2)
            buy_price = round(float(buy_stock[5]), 2)
            tmp_rate = (sell_price * (1 - 0.002)) / buy_price
            profit_rate = profit_rate * tmp_rate
            # 单次最大盈利记录
            if (tmp_rate > max_single_win_rate):
                max_single_win_rate = tmp_rate
                max_rate_buy_date = buy_stock[1]
                max_rate_sell_date = sell_stock[1]
            # 单次最大亏损记录
            if (max_single_lose_rate > tmp_rate):
                max_single_lose_rate = tmp_rate
                max_lose_rate_buy_date = buy_stock[1]
                max_lose_rate_sell_date = sell_stock[1]

            if (tmp_rate > 1):
                win_times = win_times + 1  # 盈利次数
            else:
                lose_times = lose_times + 1  # 亏损次数

        # 计算获利时,去掉本金
        max_single_win_rate = max_single_win_rate - 1
        profit_rate = profit_rate - 1
        max_single_lose_rate = max_single_lose_rate - 1

        # 插入数据库
        operatMySQl = OperateMySQL()
        sqli = "insert into {0} values ('{1}','{2}', {3},\"{4}\",\"{5}\",{6},{7},{8},{9},{10},{11},\"{12}\",\"{13}\",{14},\"{15}\",\"{16}\");"
        win_rate = 0
        if ((lose_times + win_times) > 0):
            win_rate = round(win_times / (lose_times + win_times), 3)
        sqlm = sqli.format(to_table, stock_index, key_condition, round(profit_rate, 3), start_date, end_date,
                           buy_count, sell_count, win_times, lose_times, win_rate,
                           round(max_single_win_rate, 3), max_rate_buy_date, max_rate_sell_date,
                           round(max_single_lose_rate, 3), max_lose_rate_buy_date, max_lose_rate_sell_date)
        try:
            operatMySQl.execute(sqlm)
        except:
            print("Insert Error", sqlm)

        operatMySQl.commit()
        return