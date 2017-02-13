#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' back test max lose module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from init_sql import *

class Back_Test_Stock_Rate_Macd_Deviation(Process_Job):

    #################################### 计算MACD底背离买入，macd死叉卖出收益率 ############################################
    def calculate_stock_rate_macd_deviation(self, records):
        buy_stock_list = []  # 买入列表
        sell_stock_list = []  # 卖出列表
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
        is_buy = 0
        keep_days = 0

        for row in records:
            code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
            ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[:27]

            '''
            #持有固定周期 24个
            if is_buy == 1:
                keep_days = keep_days +1
                if(keep_days>=23):
                    is_buy = 0
                    keep_days = 0
                    sell_stock_list.append((code, date, open, high, low, close, volume))
                #创新低 止损
                elif(diff < first_low_diff):
                    is_buy = 0
                    keep_days = 0
                    sell_stock_list.append((code, date, open, high, low, close, volume))
            '''
            # 死叉卖出
            if is_buy == 1:
                if (diff < dea):
                    is_buy = 0
                    sell_stock_list.append((code, date, open, high, low, close, volume))
                    # print("sell" ,code, date)
            else:
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
                        second_low_close = 0
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
                        # print("底背离:", code, get_stock_detail(code), first_golden_date, first_low_close, second_low_close, first_daed_date, date, close)
                        if is_buy == 0:
                            is_buy = 1
                            buy_stock_list.append((code, date, open, high, low, close, volume))
                            # break
                            # return
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
                        second_low_close = 0
                        first_dead = 0
                        second_green_bar_num = 0

        # 底背离尚未形成 已钝化
        # if ((first_golden == 1) and (first_dead == 1) and (
        #    second_low_close < first_low_close) and second_low_diff > first_low_diff and second_green_bar_num > 2):
        #    print("钝化:",code,get_stock_detail(code), first_golden_date, first_low_close, second_low_close, first_daed_date, date, close)

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
        buy_stock_list, sell_stock_list = self.calculate_stock_rate_macd_deviation(records)

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
        sqlm = sqli.format(to_table, stock_index, 'macd deviation', round(profit_rate, 3), start_date, end_date,
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

