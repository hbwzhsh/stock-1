import pymysql
import os
import datetime
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from cycler import cycler
import multiprocessing
from matplotlib.lines import Line2D, TICKLEFT, TICKRIGHT
import matplotlib.pyplot as plt
import numpy as np
from init_sql import *
import time
from util.dateu import *


############################################# 九转选股之日线低9  #######################################################
def dig_stock_by_nigh_times(records, times = 9, continuous_ref_times = 4):
    queue_close = []
    continuous_time = 0

    for index,row in enumerate(records):
        code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
        ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[:27]

        queue_close.append(float(close))
        if (index < (continuous_ref_times-1)):
            #交易日小于，等于4 只记录收盘价
            continue

        ref_continuous_time = True
        #for last_close in queue_close:
        last_close = queue_close[0]
        if(close > last_close):
            ref_continuous_time = False

        if(True == ref_continuous_time):
            continuous_time = continuous_time + 1
        elif(False == ref_continuous_time):
            continuous_time = 0

        #已找到符合条件个股
        if(continuous_time>= times):
            if(yesterday()<date):
                print("低九",date, get_stock_basic(code))
            continuous_time = 0
        queue_close.pop(0)


############################################# 计算MACD日线底背离 #######################################################
def dig_stock_macd_deviation(records):
    first_golden      = 0
    first_low_close   = 0.0
    first_golden_date = '1971-1-1'
    first_low_diff   = 0.0
    first_red_bar_num = 0
    second_low_diff  = 0.0
    second_low_close = 0.0
    second_green_bar_num = 0
    first_dead       = 0
    first_daed_date = '1971-1-1'

    for row in records:
        code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
        ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[:27]
        if(first_golden == 0):  #记录第一次金叉前的最小diff
            if(first_low_diff>diff):
                first_low_diff  = diff
                first_low_close = close
        elif(first_golden == 1):
            if(diff>0):    #第一次金叉后，diff穿0轴，则视为金叉无效，所有条件reset
                first_golden    = 0
                first_golden_date = '1971-1-1'
                first_low_diff  = 0
                first_low_close = 0
                first_red_bar_num = 0
                second_low_diff = 0
                second_low_close = '1971-1-1'
                first_dead = 0
                second_green_bar_num  = 0
            #记录第二次金叉前的最小diff
            if (second_low_diff > diff):
                second_low_diff  = diff
                second_low_close = close

        #第一次金叉后的red bar 连续大于0的数目
        if (bar > 0 and first_golden == 1):
            first_red_bar_num = first_red_bar_num + 1

        #diff小于0后第一次金叉后的死叉后 bar连续小于0的数目
        if(bar<0 and first_dead == 1):
            second_green_bar_num = second_green_bar_num +1

        #金叉且 diff 小于0
        if (diff > dea) and diff < 0:
            #底背离成立
            if((first_golden == 1) and (first_dead ==1) and (second_low_close< first_low_close) and second_low_diff> first_low_diff and second_green_bar_num >= 2):
                #print("底背离:", code, get_stock_detail(code), first_golden_date, first_low_close, second_low_close, first_daed_date, date, close)
                return
            #diff<0后第一次金叉
            if(first_golden == 0):
                first_golden = 1
                first_golden_date   = date
        #diff小于0后第一次金叉后的死叉
        elif (diff < dea) and diff < 0:
            if ((first_golden == 1) and (first_dead==0) and first_red_bar_num>=2):
                first_dead = 1
                first_daed_date = date
            #如果金叉后又要死叉时，绿柱数目小于2，则视为本次背离已失效，所有条件reset
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


    #底背离尚未形成 已钝化
    if ((first_golden == 1) and (first_dead == 1) and (
        second_low_close < first_low_close) and second_low_diff > first_low_diff and second_green_bar_num > 2):
        print("钝化:",code,get_stock_detail(code), first_golden_date, first_low_close, second_low_close, first_daed_date, date, close)

    return


############################################ 选估测率选股的进程壳 ######################################################
def process_dig_stock(start_date, end_date, from_table, to_table, stock_index, index, list_len):
    #打印进度 时间 ID
    #print("processed: %s%%,  Id:%s,  Time:%s" % (int((index / list_len) * 100), stock_index, (str(datetime.datetime.now()))))

    #取原始数据
    records = get_stock_ma_macd_data_from_mysql(stock_index, start_date, end_date, from_table)
    if(len(records) > 0):
        # 挖掘MACD底背离
        #dig_stock_macd_deviation(records)
        #挖掘九转出低九
        dig_stock_by_nigh_times(records, 9)

    #如果数据为0， 则不做计算并打印
    #else:
        #print("Error: get ma data is 0 (%s)" % stock_index)


########################################### 选估测率选股的多进程壳 ####################################################
def multi_process_dig_stock(start_date, end_date, from_table, mysql_table_name):
    # 获取所有股票源文件列表
    stock_file_list = get_stock_index_list_from_mysql(from_table)
    #启动多进程挖掘
    multi_process_job(process_dig_stock,stock_file_list, args=(start_date, end_date, from_table,mysql_table_name))

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    print('Start time is %s.' % (str(datetime.datetime.now())))
    start_date_list = []
    end_date_list   = []
    start_date_list.append('2016-11-1')   # 起始日期
    today = datetime.date.today().strftime("%Y-%m-%d")
    end_date_list.append(today)   # 结束日期

    from_table = 'stock_ma_macd'       #数据源
    to_table = 'stock_ma_rate'    #目标表

    #from_table = 'stock_index_ma'      #数据源
    #to_table = 'stock_index_ma_rate'  #目标表

    # 初始化要计算的股票列表
    #stock_list =get_stock_index_list_from_mysql(from_table)
    #stock_list = init_my_stock_list()

    # 挖掘股票
    for (start_date, end_date) in zip (start_date_list, end_date_list):
        print("Calculate From %s to %s" %(start_date, end_date))
        multi_process_dig_stock(start_date, end_date, from_table, to_table)
        time.sleep(30)

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))
