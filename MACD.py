#!/usr/bin/python
# -*- coding: utf-8 -*-

import tushare as ts
import matplotlib.pyplot as plt
import csv
import numpy as np
import datetime
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from cycler import cycler
import threading
import multiprocessing
from matplotlib.lines import Line2D, TICKLEFT, TICKRIGHT

###################################################### 回测 MA 值 ######################################################
def calculate_ma(df, ma_x):
    queue_close = []
    for index,row in df.iterrows():
        date, open, close, high,  low, volume, code, ma  = row[:8]
        queue_close.append(float(close))
        ma_update = sum(queue_close)/len(queue_close)
        if(index >= ma_x ):
            queue_close.pop(0)
        row['ma'] = ma_update
        df.loc[index] = row
    return df

#################################################### 回测 MA 收益率 ####################################################
def parse_stock_rate(df, stock_index, start_date, m_ma):
    is_buy    = 0
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表

    if df is None:
        return
    #df[u'close'].plot()

    rate = 1.0
    max_rate = 1.0 #单次最大收益率
    win_times = 0  #盈利次数
    lose_times = 0 #亏损次数
    #print(df)
    #df = df.sort_index(axis=0, by=None, ascending=True)
    #df = df.sort(columns = 'date',ascending=True)
    df['ma'] = 1.0
    df = calculate_ma(df, m_ma)

    for date_string,row in df.iterrows():
        date, open, close, high, low, volume, code, ma = row[:8]
        #maX =  locals()[u'ma%d' %m_ma]
        if (float(close) > ma) and (float(volume)>10000):
            if is_buy == 0:
                is_buy = 1
                buy_stock_list.append((date, open, close, high, low, volume, code, ma))
        elif (float(close) < ma) and (float(volume)>10000):
            if is_buy == 1:
                is_buy = 0
                sell_stock_list.append((date, open, close, high, low, volume, code, ma))

    #print(df)

    buy_count = len(buy_stock_list)    #买入次数
    sell_count = len(sell_stock_list)  #卖出次数

    #buy_stock_list.reverse()
    #sell_stock_list.reverse()
    max_rate_buy_date  = ''   # 单次最大盈利买入时间
    max_rate_sell_date = ''   # 单次最大盈利卖出时间

    for (buy_stock, sell_stock) in zip(buy_stock_list, sell_stock_list):
        tmp_rate = ((round(float(sell_stock[3]),2) * (1 - 0.002)) / round(float(buy_stock[3]),2))
        rate = rate * tmp_rate
        if(tmp_rate > max_rate):
            max_rate = tmp_rate
            max_rate_buy_date  = buy_stock[0]
            max_rate_sell_date = sell_stock[0]
        if( tmp_rate > 1):
            win_times = win_times   + 1   # 盈利次数
        else:
            lose_times = lose_times + 1   # 亏损次数

    print('%s Buy' %m_ma)
    print(buy_stock_list)
    print('%s Sell' %m_ma)
    print(sell_stock_list)
    #计算获利时,去掉本金
    max_rate = max_rate -1
    rate = rate - 1

    #获取股票名称
    df = ts.get_realtime_quotes(stock_index)
    stock_name = str(df['name'].values[0])

    return stock_index,stock_name, rate, buy_count, sell_count, max_rate, max_rate_buy_date,max_rate_sell_date, win_times, lose_times

#################################################### 写文件 ############################################################
def write_file_to_cvs(STOCK_RATE_LIST_SORT, MA_Time):

    # 打开要保存的结果文件
    csvfile = open("d:\\macd_result\\%d_ma.csv" % MA_Time, "w", encoding='gbk', newline='')
    writer = csv.writer(csvfile)

    # 写入文件头
    writer.writerow([u'代码', u'名称', u'收益率', u'买', u'卖', u'最大单次盈利', u'最大单次盈利买入', u'最大单次盈利卖出', u'盈利次数', u'亏损次数'])
    writer.writerows(STOCK_RATE_LIST_SORT)
    csvfile.close()

def init_my_stock_list():
    stock_list = []  # 存放股票代码列表
    stock_list.append("300287")
    stock_list.append("601198")
    #'''
    stock_list.append("300245")
    stock_list.append("300413")
    stock_list.append("300085")
    stock_list.append("002312")
    stock_list.append("600061")
    stock_list.append("300352")
    stock_list.append("300350")
    stock_list.append("600718")
    #'''
    return stock_list

#################################################### 初始化股票列表 ####################################################
def init_stock_list():
    stock_list = []  # 存放股票代码列表
    for i in range(181, 182):
        stock_list.append("30%04d" % i)
    '''
    for i in range(1, 2850):
        stock_list.append("00%04d" %i)
    #初始化创业板股票代码 列表
    for i in range(1, 600):
        stock_list.append("30%04d" %i)
    #初始化主板股票代码 列表
    for i in range(1, 2000):
        stock_list.append("60%04d" %i)
    for i in range(3000, 4000):
        stock_list.append("60%04d" %i)
    '''
    return stock_list

#################################################### 回测 MA 收益率 ####################################################
def calculate_stock(MA_Time, start_date, write_file = False):
    STOCK_RATE_LIST = []  # 存放计算结果

    # 初始化要计算的股票列表
    STOCK_LIST = init_stock_list()

    # 计算收益率
    for stock_index in STOCK_LIST:
        df = ts.get_realtime_quotes(stock_index)
        #检查股票代码是否有效
        if df is not None:
            # 计算收益率
            df = ts.get_k_data(stock_index, start_date)
            result = parse_stock_rate(df, stock_index, start_date, MA_Time)
            if result is not None:
                STOCK_RATE_LIST.append(result)

    # 按收益率排序
    STOCK_RATE_LIST_SORT = sorted(STOCK_RATE_LIST, key=lambda t: t[2], reverse=True)
    # print(STOCK_RATE_LIST_SORT)

    if (write_file == True) :
        write_file_to_cvs(STOCK_RATE_LIST_SORT, MA_Time)

################################################## 绘制MA 收益率曲线 ###################################################
def plot_stock_rate(stock_index, start_ma, end_ma, start_date, end_date):
    stock_rate = []
    ma_list = []

    my_ma_list = [2, 3, 5, 8, 10, 13, 20, 21, 30, 34, 55, 60, 89, 120]
    df = ts.get_k_data(stock_index, start_date, end_date)

    print(stock_index, df['date'][0], (str(datetime.datetime.now())))
    #周期序列
    for index in my_ma_list:
        result = parse_stock_rate(df, stock_index, start_date, index)
        if result is not None:
            ma_list.append(index)
            stock_rate.append(float(result[2]))

    # 获取股票名称
    #df = ts.get_realtime_quotes(stock_index)
    #stock_name = str(df['name'].values[0])

    return stock_index, ma_list, stock_rate


def process_plot_stock_rate(ax1, stock_list, start_ma, end_ma, start_date ):
    processes = []
    result = []
    pool = multiprocessing.Pool(4)
    max_rate = 0;
    # 计算绘制收益率
    for stock_index in stock_list:
        df = ts.get_realtime_quotes(stock_index)
        #检查股票代码是否有效
        if df is not None:
            result.append(pool.apply_async(plot_stock_rate, args=(stock_index, start_ma, end_ma , start_date, end_date)))
        #result.append(plot_stock_rate(ax1, stock_index, start_ma, end_ma, start_date))

    pool.close()
    pool.join()
    for res in result:
        # print(res.get())
        (stock_index, ma_list, stock_rate) = res.get()
        if (max_rate < float(stock_rate[0])) :
            max_rate  = float(stock_rate[0])
        #绘制曲线
        ax1.plot(ma_list, stock_rate, label=stock_index)
        ax1.annotate(stock_index, xy=(ma_list[0], stock_rate[0]), xytext=(ma_list[0] - 6, stock_rate[0] - 0.5),
                 fontsize=12, arrowprops=dict(arrowstyle="->", facecolor='blue'))  # , shrink=0.01))

    return max_rate

################################################## 初始化绘制窗口 ###################################################
def init_display(ax1, x_lim, y_lim):
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



if __name__ == '__main__':
    start_date = '2016-10-1'
    end_date   = '2016-11-11'
    max_ma = 120

    #df = ts.get_k_data('300036', start_date)
    #print(sorted(df['volume']))
    #程序开始时间
    starttime = datetime.datetime.now()
    print('Start time is %s.' % (str(datetime.datetime.now())))

    #for ma_time in range(3, 5):
    #   calculate_stock(ma_time, StartTime, True )

    #初始化显示
    ax1 = plt.subplot(111)
    init_display(ax1, x_lim = max_ma+5, y_lim = 200)

    # 初始化要计算的股票列表
    #STOCK_LIST = init_my_stock_list()
    stock_list = init_stock_list()

    # 计算绘制收益率
    max_rate = process_plot_stock_rate(ax1, stock_list, 2, max_ma+1, start_date)

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))

    ax1.set_ylim(ymax=max_rate + 2, ymin=0)
    #plt.title(stock_index) #+stock_name)
    ax1.autoscale_view()
    plt.legend()
    plt.show()
