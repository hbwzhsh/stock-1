import pymysql
import os
import datetime
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.dates import AutoDateLocator, DateFormatter
from cycler import cycler
import multiprocessing
from matplotlib.lines import Line2D, TICKLEFT, TICKRIGHT
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
from initsql import *
import time
import matplotlib as matplotlib
from matplotlib.dates import date2num


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

def init_my_stock_list():
    stock_list = []  # 存放股票代码列表

    for i in range(1, 16):
        stock_list.append("30%04d" %i)

    #stock_list.append("300001")
    #stock_list.append("300002")
    '''
    stock_list.append("300245")
    stock_list.append("300413")
    stock_list.append("300085")
    stock_list.append("002312")
    stock_list.append("600061")
    stock_list.append("300352")
    stock_list.append("300350")
    stock_list.append("600718")
    '''
    return stock_list



########################################################################################################################
#########################################        MA 回测        ########################################################
########################################################################################################################
####################################### 收盘价大于MA 买入，小于MA卖出 #################################################
def calculate_stock_rate_macd_basic( records, buy_ma, sell_ma):
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表
    close_list = []  #收盘价
    close_date = []  #收盘日期
    ma_list = []     # MA
    is_buy = 0
    sum_dif = 0
    sum_bar = 0

    for row in records:
        code, date, open, high, low, close, volume, turnover, ema12, ema26, diff, dea, bar = row[:13]

        #maX =  locals()[u'ma%d' %m_ma]
        close_list.append(close)
        close_date.append(date)
        #ma_list.append(locals()[u'ma%d' %sell_ma])

        if(not ((open == close) and (high == low) and (open == high))):
        #价格都相等时，什么都不做
        #print("All Equal open=%s close=%s high=%s low=%s" %(open, close, high, low))
        #else:
            if (float(diff) > float(dea)) and (float(volume)>10000) and(float(diff)<0):
                if is_buy == 0:
                    is_buy = 1
                    buy_stock_list.append((code, date, open, high, low, close, volume))
                    #print(date)
            elif (float(diff) < float(dea)) and (float(volume)>10000):
                if is_buy == 1:
                    is_buy = 0
                    sell_stock_list.append((code, date, open, high, low, close, volume))
        sum_dif = sum_dif + diff
        sum_bar = sum_bar + bar

    print(sum_dif, sum_bar)
    return buy_stock_list, sell_stock_list, close_list, close_date, ma_list

####################################### 收盘价大于MA 买入，小于MA卖出 #################################################
def calculate_stock_rate_ma_basic( records, buy_ma, sell_ma):
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表
    close_list = []  #收盘价
    close_date = []  #收盘日期
    ma_list = []     # MA
    is_buy = 0

    for row in records:
        code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5,\
            ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120 = row[:22]
        m_ma_buy  = locals()[u'ma%d' %buy_ma]
        m_ma_sell = locals()[u'ma%d' %sell_ma]
        #maX =  locals()[u'ma%d' %m_ma]
        close_list.append(close)
        close_date.append(date)
        ma_list.append(locals()[u'ma%d' %sell_ma])

        if(not ((open == close) and (high == low) and (open == high))):
        #价格都相等时，什么都不做
        #print("All Equal open=%s close=%s high=%s low=%s" %(open, close, high, low))
        #else:
            if (float(close) > m_ma_buy) and (float(volume)>10000):
                if is_buy == 0:
                    is_buy = 1
                    buy_stock_list.append((code, date, open, high, low, close, volume,  m_ma_buy))
            elif (float(close) < m_ma_sell) and (float(volume)>10000):
                if is_buy == 1:
                    is_buy = 0
                    sell_stock_list.append((code, date, open, high, low, close, volume, m_ma_sell))
    return buy_stock_list, sell_stock_list, close_list, close_date, ma_list

################################# 生命线MA之上 收盘价大于MA 买入，小于MA卖出 ###########################################
def calculate_stock_rate_ma_with_life( records, buy_ma, sell_ma):
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表
    close_list = []  #收盘价
    close_date = []  #收盘日期
    ma_list = []     # MA
    is_buy = 0

    for row in records:
        code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5,\
            ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120 = row[:22]

        m_ma_buy  = locals()[u'ma%d' %buy_ma]
        m_ma_sell = locals()[u'ma%d' %sell_ma]
        #maX =  locals()[u'ma%d' %m_ma]
        close_list.append(close)
        close_date.append(date)
        ma_list.append(locals()[u'ma%d' %sell_ma])

        if(not ((open == close) and (high == low) and (open == high))):
        #价格都相等时，什么都不做
        #print("All Equal open=%s close=%s high=%s low=%s" %(open, close, high, low))
        #else:
            if(float(close) >  ma21): #基准MA上操作
                if (float(close) > m_ma_buy) and (float(volume)>10000):
                    if is_buy == 0:
                        is_buy = 1
                        buy_stock_list.append((code, date, open, high, low, close, volume,  m_ma_buy))
                elif (float(close) < m_ma_sell) and (float(volume)>10000):
                    if is_buy == 1:
                        is_buy = 0
                        sell_stock_list.append((code, date, open, high, low, close, volume, m_ma_sell))
            else: #小于基准MA，强制卖出
                if is_buy == 1:
                    is_buy = 0
                    sell_stock_list.append((code, date, open, high, low, close, volume, m_ma_sell))

    return buy_stock_list, sell_stock_list, close_list, close_date, ma_list


def draw_stock_ma_rate(ax1, ax2, ax3, calculate_func,  ax_color, records, buy_ma, sell_ma):

    profit_rate = []
    single_profit_rate = []
    max_single_win_rate  = 0 #单次最大收益率
    max_single_lose_rate = 0 #单次最大亏损率
    win_times = 0    #盈利次数
    lose_times = 0   #亏损次数

    #使用策略后 获得买入卖出时间 价格列表
    buy_stock_list, sell_stock_list, close_list, close_date, ma_list = calculate_func(records, buy_ma, sell_ma)

    buy_count = len(buy_stock_list)    #买入次数
    sell_count = len(sell_stock_list)  #卖出次数

    max_rate_buy_date  = '1971-1-1'   # 单次最大盈利买入时间
    max_rate_sell_date = '1971-1-1'   # 单次最大盈利卖出时间

    max_lose_rate_buy_date  = '1971-1-1'   # 单次最大盈利买入时间
    max_lose_rate_sell_date = '1971-1-1'   # 单次最大盈利卖出时间
    sell_stock_date_list = []

    total_profit = 1   #总收益率
    max_profit = 0     #收益率最大值

    #统计 计算结果
    for (buy_stock, sell_stock) in zip(buy_stock_list, sell_stock_list):
        sell_price = round(float(sell_stock[5]), 2)  #卖出价格
        buy_price  = round(float(buy_stock[5]), 2)   #买入价格
        tmp_rate = (sell_price * (1 - 0.002)) / buy_price  #收益率
        total_profit = total_profit * tmp_rate        #总收益率
        tmp_rate = tmp_rate - 1               #去除本金
        single_profit_rate.append(tmp_rate)   #买次盈亏率
        profit_rate.append(total_profit)      #加入总盈利表
        sell_stock_date_list.append(sell_stock[1]) #卖出日期表
        #设置盈亏使用不同的颜色标识
        alpha = 0.2
        color = 'r'
        if(tmp_rate<0):
            color = 'g'

        # 最大盈利值
        if (total_profit > max_profit):
            max_profit = total_profit
        # 单次最大盈利记录
        if (tmp_rate > max_single_win_rate):
            max_single_win_rate = tmp_rate
            max_rate_buy_date = buy_stock[1]
            max_rate_sell_date = sell_stock[1]
            color = 'b'
            alpha = 0.5
            # print("win:", sell_price, buy_price, max_rate_buy_date, max_rate_sell_date)

        # 单次最大亏损记录
        if (max_single_lose_rate > tmp_rate):
            max_single_lose_rate = tmp_rate
            max_lose_rate_buy_date = buy_stock[1]
            max_lose_rate_sell_date = sell_stock[1]
            color = 'b'
            alpha = 0.5

            # print("lost:", sell_price, buy_price, max_lose_rate_buy_date, max_lose_rate_sell_date)

        if (tmp_rate > 0):
            win_times = win_times + 1  # 盈利次数
        else:
            lose_times = lose_times + 1  # 亏损次数
        '''
        rect_profit = Rectangle(
            xy=(date2num(buy_stock[1]), 0),
            width=date2num(sell_stock[1]) - date2num(buy_stock[1]),
            height=total_profit,
            facecolor=color,
            edgecolor=color,
        )
        rect_profit.set_alpha(1.0)
        ax2.add_patch(rect_profit)
        '''
        ax2.text(sell_stock[1], total_profit+1, round(tmp_rate, 3),bbox=dict(color=color, alpha=alpha))


    #计算获利时,去掉本金
    max_single_win_rate = max_single_win_rate
    #profit_rate = profit_rate - 1

    #print(max_lose_rate_buy_date, max_lose_rate_sell_date, max_single_lose_rate)
    max_single_lose_rate = max_single_lose_rate

    # 绘制收益率曲线
    ax1.plot(close_date, close_list, color='r')
    #ax1.plot(close_date, ma_list, color='b')
    # ax1.set_ylim(ymax=max_single_win_rate + 1, ymin=max_single_lose_rate)

    ax2.plot(sell_stock_date_list, profit_rate, color = ax_color, marker ='o' )
    #out_str = "Toal_Win: {0}\nWin_tims: {1}\nWin_rate: {2}\nMax_win: {3}\nMax_lost: {4}".format\
    #    (round(total_profit, 3), win_times, round(win_times/(win_times+lose_times), 3), round(max_single_win_rate,3), round(max_single_lose_rate,3))
    #ax2.text(sell_stock_date_list[1], total_profit*0.9, out_str, fontsize=14, bbox=dict(color=ax_color, alpha=0.2))
    #ax2.set_ylim(ymax=total_profit + 5, ymin=-1)

    #绘制单次收益率
    ax3.plot(sell_stock_date_list, single_profit_rate, color = ax_color, )
    single_profit_rate =  [0]*len(single_profit_rate);
    ax3.plot(sell_stock_date_list, single_profit_rate, color='k')    #画0轴
    out_str = "Buy_ma: {0}\nSell_ma: {1}".format\
        (buy_ma, sell_ma)
    ax3.text(sell_stock_date_list[1], max_single_win_rate*.8 , out_str, fontsize=14, bbox=dict(color='g', alpha=0.2))

    #ax3.set_ylim(ymax=max_single_win_rate + 1 , ymin = max_single_lose_rate )

    return



################################################## 初始化绘制窗口 ###################################################
def init_display(x_lim, y_lim):

    #设定plot窗口为1个
    #ax1 = plt.subplot(111)
    #(ax1, ax2) = plt.subplots(2, sharex=True)
    ax1 = plt.subplot(311)  # 在图表2中创建子图1
    ax2 = plt.subplot(312)  # 在图表2中创建子图2
    ax3 = plt.subplot(313)  # 在图表2中创建子图2

    # 调整绘图窗口颜色及显示范围
    samples = range(1, 16)
    colormap = plt.cm.Paired
    plt.gca().set_prop_cycle(cycler('color', [colormap(i) for i in np.linspace(0, 0.9, len(samples))]))
    plt.subplots_adjust(wspace=None, hspace=0.0001, top=0.95, bottom=0.02, left=0.03, right=0.98)

    '''
    xmajorLocator = MultipleLocator(5)  # 将x主刻度标签设置为5的倍数
    #xmajorFormatter = FormatStrFormatter('%1.1f')  # 设置x轴标签文本的格式
    xminorLocator = MultipleLocator(1)  # 将x轴次刻度标签设置为1的倍数
    '''
    autodates = AutoDateLocator()
    yearsFmt =  DateFormatter('%Y-%m-%d')
    #plt.autofmt_xdate()  # 设置x轴时间外观

    for ax in (ax1, ax2, ax3):
        ax.xaxis.set_major_locator(autodates)  # 设置时间间隔
        ax.xaxis.set_major_formatter(yearsFmt)  # 设置时间显示格式

    ymajorLocator_1   = MultipleLocator(5)  # 将y轴主刻度标签设置为1的倍数
    ymajorFormatter_1 = FormatStrFormatter('%1.1f')  # 设置y轴标签文本的格式
    yminorLocator_1   = MultipleLocator(1)  # 将此y轴次刻度标签设置为0.5的倍数


    ymajorLocator_2   = MultipleLocator(2)  # 将y轴主刻度标签设置为1的倍数
    ymajorFormatter_2 = FormatStrFormatter('%1.1f')  # 设置y轴标签文本的格式
    yminorLocator_2   = MultipleLocator(0.5)  # 将此y轴次刻度标签设置为0.5的倍数

    ymajorLocator_3   = MultipleLocator(0.2)  # 将y轴主刻度标签设置为1的倍数
    ymajorFormatter_3 = FormatStrFormatter('%1.1f')  # 设置y轴标签文本的格式
    yminorLocator_3   = MultipleLocator(0.1)  # 将此y轴次刻度标签设置为0.5的倍数


    ax1.yaxis.set_major_locator(ymajorLocator_1)
    ax1.yaxis.set_major_formatter(ymajorFormatter_1)
    ax1.yaxis.set_minor_locator(yminorLocator_1)
    #ax1.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
    #ax1.yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度

    ax2.yaxis.set_major_locator(ymajorLocator_2)
    ax2.yaxis.set_major_formatter(ymajorFormatter_2)
    ax2.yaxis.set_minor_locator(yminorLocator_2)
    #ax2.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
    #ax2.yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度

    # 设置主刻度标签的位置,标签文本的格式
    #ax1.xaxis.set_major_locator(xmajorLocator)
    # plt.xaxis.set_major_formatter(xmajorFormatter)

    ax3.yaxis.set_major_locator(ymajorLocator_3)
    ax3.yaxis.set_major_formatter(ymajorFormatter_3)

    # 显示次刻度标签的位置,没有标签文本
    #ax1.xaxis.set_minor_locator(xminorLocator)
    ax3.yaxis.set_minor_locator(yminorLocator_3)

    for ax in (ax1,ax2,ax3):
        ax.xaxis.grid(True, which='major')  # x坐标轴的网格使用主刻度
        ax.yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度
        ax.yaxis.grid(True, which='minor')  # y坐标轴的网格使用次刻度

    #ax1.set_xlim(xmax=x_lim, xmin=-6)
    #ax1.set_ylim(ymax=y_lim, ymin=0)

    return ax1, ax2, ax3

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    zhfont = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simsun.ttc')
    print('Start time is %s.' % (str(datetime.datetime.now())))
    start_date_list = []
    end_date_list   = []
    calculate_func_list  = []

    start_date_list.append('2016-1-1')
    end_date_list.append('2016-3-31')

    start_date_list.append('2016-4-1')
    end_date_list.append('2016-6-31')

    start_date_list.append('2016-6-1')
    end_date_list.append('2016-9-31')

    start_date_list.append('2016-10-1')
    end_date_list.append('2016-11-18')

    start_date_list.append('2016-1-1')
    end_date_list.append('2016-11-18')

    from_table = 'stock_ma'       #数据源
    to_table   = 'stock_ma_rate'    #目标表

    draw_plot = True   #是否绘制收益率曲线

    # 初始化显示
    if (draw_plot == True):
        ax1, ax2, ax3  = init_display(x_lim= 5, y_lim=200)

    # 初始化要计算的股票列表
    #stock_list =get_stock_index_list_from_mysql(from_table)
    #stock_list = init_my_stock_list()

    # 绘制收益率
    stock_index = '300085'
    start_date = '2014-7-1'
    end_date   = '2016-11-18'
    buy_ma     = 5
    sell_ma    = 5
    calculate_func_list.append((calculate_stock_rate_ma_basic, 'b'))
    calculate_func_list.append((calculate_stock_rate_ma_with_life, 'r'))
    #calculate_func_list.append((calculate_stock_rate_macd_basic, 'g'))

    records = get_stock_ma_data_from_mysql(stock_index, start_date, end_date, from_table)
    for calculate_func in calculate_func_list:
        draw_stock_ma_rate(ax1, ax2, ax3, calculate_func[0], calculate_func[1],  records, buy_ma, sell_ma)

    records = get_stock_ma_data_from_mysql(stock_index, start_date, end_date, 'stock_macd')
    draw_stock_ma_rate(ax1, ax2, ax3, calculate_stock_rate_macd_basic, 'g', records, buy_ma, sell_ma)

    record = get_stock_detail(stock_index)
    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))

    if(draw_plot == True):
        #ax1.set_ylim(ymax=max_rate + 2, ymin=-6)
        #plt.title(stock_index) #+stock_name)
        ax1.set_title(record[0][1] + '  ' + stock_index, fontproperties=zhfont, fontsize=15, fontweight=5)
        ax1.autoscale_view()
        ax2.autoscale_view()
        ax3.autoscale_view()
        plt.legend()
        plt.show()