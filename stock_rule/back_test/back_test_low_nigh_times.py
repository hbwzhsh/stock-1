#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' back test max lose module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from init_sql import *

class Back_Test_Low_Nigh_Times(Process_Job):

    ############################################# 九转选股之日线低9  #######################################################
    def dig_stock_by_nigh_times(self,records, times=13, continuous_ref_times=4):
        buy_stock_list = []  # 买入列表
        sell_stock_list = []  # 卖出列表
        queue_close = []
        continuous_time = 0
        is_buy = 0
        day_num_after_buy = 0
        keep_stock_days = 13

        for index, row in enumerate(records):
            code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
            ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[:27]

            queue_close.append(float(close))
            if (index < (continuous_ref_times - 1)):
                # 交易日小于，等于4 只记录收盘价
                continue
            # 符合条件，买入后持有至keep_stock_days结束后卖出
            if is_buy == 1:
                day_num_after_buy = day_num_after_buy + 1
                if day_num_after_buy > keep_stock_days:
                    is_buy = 0
                    day_num_after_buy = 0
                    sell_stock_list.append((code, date, open, high, low, close, volume))
            elif is_buy == 0:
                # 今日收盘价 低于 continuous_ref_times 日之前的收盘价，连续符合本条件times 次后买入
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
                    # print(date, get_stock_detail(code))
                    # if is_buy == 0:
                    is_buy = 1
                    continuous_time = 0
                    buy_stock_list.append((code, date, open, high, low, close, volume))
            queue_close.pop(0)

        return buy_stock_list, sell_stock_list

    def process(self, start_date, end_date, from_table, to_table, stock_index, index, list_len):

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
        buy_stock_list, sell_stock_list = self.dig_stock_by_nigh_times(records, 9)

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
        sqlm = sqli.format(to_table, stock_index, 'low 9', round(profit_rate, 3), start_date, end_date,
                           buy_count, sell_count, win_times, lose_times, win_rate,
                           round(max_single_win_rate, 3), max_rate_buy_date, max_rate_sell_date,
                           round(max_single_lose_rate, 3), max_lose_rate_buy_date, max_lose_rate_sell_date)
        try:
            operatMySQl.execute(sqlm)
        except:
            print("Insert Error", sqlm)

        operatMySQl.commit()
        return


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

