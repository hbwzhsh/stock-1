#!/usr/bin/env python3
# -*- coding: utf-8 -*-
' back test model '
__author__ = 'Yuechen Yang'

import time

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

from stock_rule.back_test.back_test_low_nigh_times import *
from stock_rule.back_test.back_test_stock_rate_macd_deviation import *
from stock_rule.back_test.back_test_stock_rate_macd_basic import *
from stock_rule.back_test.back_test_calculat_stock_max_lose import *
from stock_rule.back_test.back_test_calculate_stock_rate_ma_basic import *
from stock_rule.back_test.back_test_calculate_max_limit_rate import *
from util.dateu import *
from util.multi_processes import *

#################################################### 初始化股票列表 ####################################################
def init_stock_list_for_convert():
    stock_list = []  # 存放股票代码列表

    for i in range(1, 2850):
        stock_list.append("SZ#00%04d.txt" %i)
    #初始化创业板股票代码 列表
    for i in range(1, 600):
        stock_list.append("SZ#30%04d.txt" %i)

    #初始化主板股票代码 列表
    for i in range(1, 2000):
        stock_list.append("SH#60%04d.txt" %i)
    for i in range(3000, 4000):
        stock_list.append("SH#60%04d.txt" %i)

    return stock_list


#@log_date_time
def analyze_result():
    operatMySQl = OperateMySQL()
    analyze_table = 'stock_win_rate'

    # 大于0的数据个数
    operatMySQl.execute("SELECT count(*)  FROM %s where profit_rate >0;" %analyze_table)
    records = operatMySQl.fetchall()
    print("大于0：", records[0][0])

    operatMySQl.execute("SELECT count(*)  FROM %s where profit_rate >0 and stock_index > 300000 and stock_index < 400000" %analyze_table)
    records = operatMySQl.fetchall()
    print("创业板：", records[0][0])

    operatMySQl.execute("SELECT count(*)  FROM %s where profit_rate >0 and stock_index > 600000 and stock_index < 700000" %analyze_table)
    records = operatMySQl.fetchall()
    print("沪市：", records[0][0])

    operatMySQl.execute("SELECT count(*)  FROM %s where profit_rate >0 and stock_index > 000000 and stock_index < 100000" %analyze_table)
    records = operatMySQl.fetchall()
    print("深市：", records[0][0])

    operatMySQl.execute("SELECT count(*)  FROM %s where profit_rate <0 ;" %analyze_table)
    records = operatMySQl.fetchall()
    print("小于0：", records[0][0])

    operatMySQl.execute("SELECT count(*)  FROM %s where profit_rate <0 and stock_index > 300000 and stock_index < 400000" %analyze_table)
    records = operatMySQl.fetchall()
    print("创业板：", records[0][0])

    operatMySQl.execute("SELECT count(*)  FROM %s where profit_rate <0 and stock_index > 600000 and stock_index < 700000" %analyze_table)
    records = operatMySQl.fetchall()
    print("沪市：", records[0][0])

    operatMySQl.execute("SELECT count(*)  FROM %s where profit_rate <0 and stock_index > 000000 and stock_index < 100000" %analyze_table)
    records = operatMySQl.fetchall()
    print("深市：", records[0][0])

    return records

##################################### 启动多进程任务转换通达信数据并插入数据库 #########################################
def process_calculate_stock(start_date, end_date, from_table, to_table):

    if 0 :
        clear_table('stock_win_rate')  # 清除数据
        # 九转回测
        Back_Test_Low_Nigh_Times(start_date, end_date, from_table, to_table).run_multi_process_job()

        # MACD 底背离回测
        Back_Test_Stock_Rate_Macd_Deviation(start_date, end_date, from_table, to_table).run_multi_process_job()

        # 计算MACD金叉买入，macd死叉卖出收益率
        Back_Test_Stock_Rate_Macd_Basic(start_date, end_date, from_table, to_table).run_multi_process_job()

        # 计算大于MA周期买入，小于MA周期卖出
        Back_Test_Calculate_Stock_Rate_MA_Basic(start_date, end_date, from_table, to_table, buy_ma =2, sell_ma=2).run_multi_process_job()

    if 1:
        clear_table('stock_temp_rate')  #清除数据
        # 计算一段时间内最大跌幅
        Back_Test_Calculat_Stock_Max_Lose('2016-5-1', end_date, from_table, 'stock_temp_rate').run_multi_process_job()

        #计算一段时间内的涨停率
        #Back_Test_Calculat_Max_Limit_Rate(start_date, end_date, from_table, 'stock_temp_rate').run_multi_process_job()


################################################## 初始化绘制窗口 ###################################################
def init_display(x_lim, y_lim):

    #设定plot窗口为1个
    ax1 = plt.subplot(111)

    # 调整绘图窗口颜色及显示范围
    samples = range(1, 16)
    colormap = plt.cm.Paired
    plt.gca().set_prop_cycle(cycler('color', [colormap(i) for i in np.linspace(0, 0.9, len(samples))]))
    plt.subplots_adjust(wspace=None, hspace=0.0001, top=0.98, bottom=0.02, left=0.03, right=0.98)

    xmajorLocator = MultipleLocator(5)  # 将x主刻度标签设置为5的倍数
    #xmajorFormatter = FormatStrFormatter('%1.1f')  # 设置x轴标签文本的格式
    xminorLocator = MultipleLocator(1)  # 将x轴次刻度标签设置为1的倍数

    ymajorLocator = MultipleLocator(5)  # 将y轴主刻度标签设置为1的倍数
    ymajorFormatter = FormatStrFormatter('%1.1f')  # 设置y轴标签文本的格式
    yminorLocator = MultipleLocator(1)  # 将此y轴次刻度标签设置为0.5的倍数

    # 设置主刻度标签的位置,标签文本的格式
    ax1.xaxis.set_major_locator(xmajorLocator)
    # plt.xaxis.set_major_formatter(xmajorFormatter)

    ax1.yaxis.set_major_locator(ymajorLocator)
    ax1.yaxis.set_major_formatter(ymajorFormatter)

    # 显示次刻度标签的位置,没有标签文本
    ax1.xaxis.set_minor_locator(xminorLocator)
    ax1.yaxis.set_minor_locator(yminorLocator)

    ax1.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
    ax1.yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度

    ax1.set_xlim(xmax=x_lim, xmin=-6)
    ax1.set_ylim(ymax=y_lim, ymin=0)

    return ax1

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    print('Start time is %s.' % (str(datetime.datetime.now())))
    start_date_list = []
    end_date_list   = []
    start_date_list.append('2011-1-1')   # 起始日期
    today = datetime.date.today().strftime("%Y-%m-%d")
    end_date_list.append(today)   # 结束日期
    '''
    start_date_list.append('2015-6-15')  # 起始日期
    end_date_list.append('2016-3-15')    # 结束日期

    start_date_list.append('2016-1-28')  # 起始日期
    end_date_list.append('2016-11-18')   # 结束日期

    start_date_list.append('2013-7-1')   # 起始日期
    end_date_list.append('2016-11-18')   # 结束日期

    start_date_list.append('2011-7-1')   # 起始日期
    end_date_list.append('2016-11-18')   # 结束日期
    '''
    #start_date_list.append('1990-1-1')   # 起始日期
    #end_date_list.append('2016-11-18')   # 结束日期
    #'''
    max_ma = 120
    from_table = 'stock_ma_macd'       #数据源
    to_table = 'stock_win_rate'    #目标表

    #from_table = 'stock_index_ma'      #数据源
    #to_table = 'stock_index_ma_rate'  #目标表

    draw_plot = False   #是否绘制收益率曲线

    # 初始化显示
    if (draw_plot == True):
        ax1 = init_display(x_lim=max_ma + 5, y_lim=200)

    # 计算收益率
    #max_rate = process_plot_stock_rate(ax1, stock_list, start_date, end_date, draw_plot, from_table, to_table)
    for (start_date, end_date) in zip (start_date_list, end_date_list):
        print("Calculate From %s to %s" %(start_date, end_date))
        process_calculate_stock(start_date, end_date, from_table, to_table)
        time.sleep(30)

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))

    #结果
    analyze_result()

    if(draw_plot == True):
        #ax1.set_ylim(ymax=max_rate + 2, ymin=-6)
        # plt.title(stock_index) #+stock_name)
        ax1.autoscale_view()
        plt.legend()
        plt.show()