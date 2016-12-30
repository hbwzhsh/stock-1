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
#########################################         回测涨停率        ####################################################
########################################################################################################################
def calculat_stock_max_times(records):
    limit_up_times = 0
    limit_down_times = 0
    last_close = 0
    launch_date = '1971-1-1'
    for index,row in enumerate(records):
        code, date, open, high, low, close, volume, turnover = row[:8]
        if(index<1):
            last_close = close
            launch_date = date
            continue
        if(((close-last_close)/last_close)>0.091) :
            limit_up_times = limit_up_times +1
        elif(((close-last_close)/last_close)< -0.091) :
            limit_down_times = limit_down_times +1
        last_close = close

    return index, launch_date,limit_up_times, my_round(limit_up_times/index), limit_down_times, my_round(limit_down_times/index)

###################################### 计算某支股票的指定MA策略买卖数据 ################################################
def calculat_stock_rate(calculate_func, records, stock_index, to_table):


    #使用策略后 获得买入卖出时间 价格列表
    deal_days, launch_date, limit_up_times, limit_up_times_rate, limit_down_times, limit_down_times_rate = calculate_func(records)

    # 插入数据库
    conn = pymysql.connect(user='root', host='localhost', passwd='123456', db='stock', charset="utf8")
    cur = conn.cursor()
    sqli = "insert into {0} values ('{1}',{2},\"{3}\",{4},{5},{6},{7});"
    sqlm = sqli.format(to_table,stock_index, deal_days, launch_date, limit_up_times, limit_up_times_rate, limit_down_times, limit_down_times_rate)
    try:

        cur.execute(sqlm)
        # print(sqlm)
    except:
        print("Insert Error", sqlm)

    conn.commit()
    if cur and conn:
        cur.close()
        conn.close()

    return

########################################################################################################################
#########################################           回测        ########################################################
########################################################################################################################

############################################# 九转选股之日线低9  #######################################################
def dig_stock_by_nigh_times(records, buy_ma, sell_ma, times = 13, continuous_ref_times = 4):
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表
    queue_close = []
    continuous_time = 0
    is_buy = 0
    day_num_after_buy = 0
    keep_stock_days = 13

    for index,row in enumerate(records):
        code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
        ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[:27]

        queue_close.append(float(close))
        if (index < (continuous_ref_times-1)):
            #交易日小于，等于4 只记录收盘价
            continue
        #符合条件，买入后持有至keep_stock_days结束后卖出
        if is_buy == 1:
            day_num_after_buy = day_num_after_buy + 1
            if day_num_after_buy > keep_stock_days:
                is_buy = 0
                day_num_after_buy = 0
                sell_stock_list.append((code, date, open, high, low, close, volume))
        elif is_buy == 0:
            #今日收盘价 低于 continuous_ref_times 日之前的收盘价，连续符合本条件times 次后买入
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
                #print(date, get_stock_detail(code))
                #if is_buy == 0:
                is_buy = 1
                continuous_time = 0
                buy_stock_list.append((code, date, open, high, low, close, volume))
        queue_close.pop(0)

    return buy_stock_list, sell_stock_list

#################################### 计算MACD底背离买入，macd死叉卖出收益率 ############################################
def calculate_stock_rate_macd_deviation( records, buy_ma, sell_ma):
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表
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
    is_buy = 0

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
                if is_buy == 0:
                    is_buy = 1
                    buy_stock_list.append((code, date, open, high, low, close, volume))
                    #break
                #return
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

        if (diff < dea):
            if is_buy == 1:
                is_buy = 0
                sell_stock_list.append((code, date, open, high, low, close, volume))
                #print("sell" ,code, date)

    #底背离尚未形成 已钝化
    #if ((first_golden == 1) and (first_dead == 1) and (
    #    second_low_close < first_low_close) and second_low_diff > first_low_diff and second_green_bar_num > 2):
    #    print("钝化:",code,get_stock_detail(code), first_golden_date, first_low_close, second_low_close, first_daed_date, date, close)

    return buy_stock_list, sell_stock_list

####################################### MACD金叉买入，MACD死叉卖出 #################################################
def calculate_stock_rate_macd_basic( records, buy_ma, sell_ma):
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表
    is_buy = 0

    for row in records:
        code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, \
        ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = row[:27]

        if(not ((open == close) and (high == low) and (open == high))):
        #价格都相等时，什么都不做
        #print("All Equal open=%s close=%s high=%s low=%s" %(open, close, high, low))
        #else:
            if (float(diff) > float(dea)) and (float(volume)>10000): # and(float(diff)<0):
                if is_buy == 0:
                    is_buy = 1
                    buy_stock_list.append((code, date, open, high, low, close, volume))
                    #print(date)
            elif (float(diff) < float(dea)) and (float(volume)>10000):
                if is_buy == 1:
                    is_buy = 0
                    sell_stock_list.append((code, date, open, high, low, close, volume))

    return buy_stock_list, sell_stock_list

####################################### 收盘价大于MA 买入，小于MA卖出 #################################################
def calculate_stock_rate_ma_basic( records, buy_ma, sell_ma):
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表
    is_buy = 0

    for row in records:
        code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5,\
            ma8, ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120 = row[:22]
        m_ma_buy  = locals()[u'ma%d' %buy_ma]
        m_ma_sell = locals()[u'ma%d' %sell_ma]

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
    return buy_stock_list, sell_stock_list

###################################### 计算某支股票的指定MA策略买卖数据 ################################################
def calculat_stock_ma_rate(calculate_func, records, stock_index, start_date, end_date, buy_ma, sell_ma, to_table):
    buy_stock_list  = [] #买入列表
    sell_stock_list = [] #卖出列表
    profit_rate = 1.0
    max_single_win_rate = 1.0 #单次最大收益率
    max_single_lose_rate = 1.0 #单次最大亏损率
    win_times = 0  #盈利次数
    lose_times = 0 #亏损次数

    #print(" Id:%s,  Enter Time:%s" % (stock_index, (str(datetime.datetime.now()))))

    #使用策略后 获得买入卖出时间 价格列表
    buy_stock_list, sell_stock_list= calculate_func(records, buy_ma, sell_ma)

    buy_count = len(buy_stock_list)    #买入次数
    sell_count = len(sell_stock_list)  #卖出次数

    max_rate_buy_date  = '1971-1-1'   # 单次最大盈利买入时间
    max_rate_sell_date = '1971-1-1'   # 单次最大盈利卖出时间

    max_lose_rate_buy_date  = '1971-1-1'   # 单次最大盈利买入时间
    max_lose_rate_sell_date = '1971-1-1'   # 单次最大盈利卖出时间

    for (buy_stock, sell_stock) in zip(buy_stock_list, sell_stock_list):
        sell_price = round(float(sell_stock[5]), 2)
        buy_price = round(float(buy_stock[5]), 2)
        tmp_rate = (sell_price * (1 - 0.002)) / buy_price
        profit_rate = profit_rate * tmp_rate
        #单次最大盈利记录
        if(tmp_rate > max_single_win_rate):
            max_single_win_rate = tmp_rate
            max_rate_buy_date  = buy_stock[1]
            max_rate_sell_date = sell_stock[1]
        #单次最大亏损记录
        if(max_single_lose_rate > tmp_rate):
            max_single_lose_rate = tmp_rate
            max_lose_rate_buy_date  = buy_stock[1]
            max_lose_rate_sell_date = sell_stock[1]

        if( tmp_rate > 1):
            win_times = win_times   + 1   # 盈利次数
        else:
            lose_times = lose_times + 1   # 亏损次数

    #计算获利时,去掉本金
    max_single_win_rate = max_single_win_rate -1
    profit_rate = profit_rate - 1
    max_single_lose_rate = max_single_lose_rate -1

    #'''
    #插入数据库
    conn = pymysql.connect(user='root', host='localhost', passwd='123456', db='stock', charset="utf8")
    cur = conn.cursor()
    sqli = "insert into {0} values ('{1}',{2},{3},{4},\"{5}\",\"{6}\",{7},{8},{9},{10},{11},{12},\"{13}\",\"{14}\",{15},\"{16}\",\"{17}\");"
    win_rate = 0
    if((lose_times + win_times)>0):
        win_rate = round( win_times/(lose_times + win_times), 3)
    sqlm = sqli.format(to_table, stock_index, round(profit_rate,3), buy_ma, sell_ma, start_date, end_date, buy_count, sell_count, win_times, lose_times, win_rate,
                       round(max_single_win_rate, 3), max_rate_buy_date, max_rate_sell_date,
                       round(max_single_lose_rate,3),  max_lose_rate_buy_date, max_lose_rate_sell_date)
    try:
        #print(" Id:%s,  Exit Time:%s" % (stock_index, (str(datetime.datetime.now()))))
        cur.execute(sqlm)
        #print(sqlm)
    except:
        print("Insert Error", sqlm)

    conn.commit()
    if cur and conn:
        cur.close()
        conn.close()
    #'''
    return


######################################## 计算某支股票的MA策略买卖数据 ##################################################
def process_calculate_stock_ma_macd_rate(start_date, end_date, from_table, to_table, stock_index, index, list_len):
    buy_ma_list = [2, 3, 5, 8, 10, 13, 20, 21, 30, 34, 55, 60, 89, 120]    #周期序列
    sell_ma_list = [2, 3, 5, 8, 10, 13, 20, 21, 30, 34, 55, 60, 89, 120]   #周期序列
    max_times_list = []

    #打印进度 时间 ID
    print("processed: %s%%,  Id:%s,  Time:%s" % (int((index / list_len) * 100), stock_index, (str(datetime.datetime.now()))))

    #取原始数据
    #records = get_stock_ma_macd_data_from_mysql(stock_index, start_date, end_date, from_table)
    records = get_stock_all_data_from_mysql_stock_index(stock_index)
    if(len(records) > 0):
        '''
        # 数据有效计算Ma收益率
        for (buy_ma, sell_ma) in zip (buy_ma_list, sell_ma_list):
            calculat_stock_ma_rate(calculate_stock_rate_ma_basic, records, stock_index, start_date, end_date, buy_ma, sell_ma, to_table)

        #计算MACD 金叉买入, 死叉卖出收益率
        calculat_stock_ma_rate(calculate_stock_rate_macd_basic, records, stock_index, start_date, end_date, 0, 0, to_table)
        '''
        # 计算MACD底背离买入，macd死叉卖出收益率
        #calculat_stock_ma_rate(calculate_stock_rate_macd_deviation, records, stock_index, start_date, end_date, 1, 1, to_table)

        # 计算九转低九后 持股N日 收益率
        #calculat_stock_ma_rate(dig_stock_by_nigh_times, records, stock_index, start_date, end_date, 9, 9, to_table)
        #calculat_stock_ma_rate(dig_stock_by_nigh_times, records, stock_index, start_date, end_date, 13, 13, to_table)
        calculat_stock_rate(calculat_stock_max_times, records, stock_index, 'stock_temp_rate')

    #如果数据为0， 则不做计算并打印
    #else:
        #print("Error: get ma data is 0 (%s)" % stock_index)


##################################### 启动多进程任务转换通达信数据并插入数据库 #########################################
def multi_process_calculate_stock_ma_macd_rate(start_date, end_date, from_table, mysql_table_name):
    # 获取所有股票源文件列表
    stock_file_list = get_stock_index_list_from_mysql(from_table)
    #stock_file_list = init_my_stock_list()
    #启动多进程
    multi_process_job(process_calculate_stock_ma_macd_rate,stock_file_list, args=(start_date, end_date, from_table,mysql_table_name))



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
    start_date_list.append('2013-1-1')   # 起始日期
    today = datetime.date.today().strftime("%Y-%m-%d")
    end_date_list.append(today)   # 结束日期
    '''
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

    start_date_list.append( '2011-7-1')
    end_date_list.append('2014-7-1')

    start_date_list.append('2014-7-1')
    end_date_list.append('2015-6-15')

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
    to_table = 'stock_ma_rate'    #目标表

    #from_table = 'stock_index_ma'      #数据源
    #to_table = 'stock_index_ma_rate'  #目标表

    draw_plot = False   #是否绘制收益率曲线

    # 初始化显示
    if (draw_plot == True):
        ax1 = init_display(x_lim=max_ma + 5, y_lim=200)

    # 初始化要计算的股票列表
    #stock_list =get_stock_index_list_from_mysql(from_table)
    #stock_list = init_my_stock_list()

    # 计算收益率
    #max_rate = process_plot_stock_rate(ax1, stock_list, start_date, end_date, draw_plot, from_table, to_table)
    for (start_date, end_date) in zip (start_date_list, end_date_list):
        print("Calculate From %s to %s" %(start_date, end_date))
        multi_process_calculate_stock_ma_macd_rate(start_date, end_date, from_table, to_table)
        time.sleep(30)

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))

    if(draw_plot == True):
        #ax1.set_ylim(ymax=max_rate + 2, ymin=-6)
        # plt.title(stock_index) #+stock_name)
        ax1.autoscale_view()
        plt.legend()
        plt.show()