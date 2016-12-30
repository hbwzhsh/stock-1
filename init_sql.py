#!/usr/bin/python
# -*- coding: utf-8 -*-

import pymysql
import os
import datetime
import tushare as ts
import csv
import multiprocessing
from decimal import *
from util.operate_mysql import *
from util import vars as vs


############################################### 多进程通用接口 #########################################################
def multi_process_job(func, iterate_list, args=()):
    pool = multiprocessing.Pool(vs.MULTI_PROCESS_NUMBER)
    result = []
    index = 0
    list_len = len(iterate_list)
    process_percent = 0
    for list_index in iterate_list:
        index = index + 1
        result.append( pool.apply_async(func, args=(args+(list_index, index, list_len))))

    pool.close()
    pool.join()

def get_stock_detail(stock_index):
    conn, cur = open_mysql()

    sql = "SELECT *  FROM stock_detail where stock_index ='{0}';"
    sql = sql.format(stock_index)
    # print(sql)
    cur.execute(sql)
    records = cur.fetchall()

    close_mysql(conn, cur)

    return records

def get_stock_basic(stock_index):
    conn, cur = open_mysql()

    sql = "SELECT *  FROM stock_basic where stock_index ='{0}';"
    sql = sql.format(stock_index)
    # print(sql)
    cur.execute(sql)
    records = cur.fetchall()

    close_mysql(conn, cur)
    stock_index, name, industry, area, pe, outstanding, totals, totalAssets, liquidAssets, fixedAssets, reserved,\
        reservedPerShare, esp, bvps, pb, timeToMarket, undp, perundp, rev, profit, gpr, npr, holders, = records[0][:23]
    info = "{0}, {1:<5}, {2:<4}, 市盈率：{3}, 流通(亿)：{4} 总股本(亿)：{5}，每股公积金：{6}, 每股收益：{7} 每股净资：{8}，市净率：{9}， 上市日期：{10}， 每股未分配：{11}"
    info = info.format(stock_index, name, industry,pe, outstanding, totals,reservedPerShare,esp, bvps, pb,timeToMarket,perundp)
    return info

################################# 从数据库指定的表依据指定条件取出某支股票数据 #########################################
def get_stock_ma_macd_data_from_mysql(stock_index, start_date, end_date, from_table):
    conn, cur = open_mysql()

    sql = "SELECT *  FROM stock_raw_data natural join {0} where stock_index ='{1}' and (date>='{2}' and date <= '{3}')"
    sql = sql.format(from_table, stock_index, start_date, end_date)
    #print(sql)
    cur.execute(sql)
    records = cur.fetchall()

    close_mysql(conn, cur)

    return records

def get_stock_all_data_from_mysql_stock_index(stock_index):
    conn, cur = open_mysql()

    sql = "SELECT *  FROM stock_raw_data where stock_index ='{0}' "
    sql = sql.format(stock_index)
    #print(sql)
    cur.execute(sql)
    records = cur.fetchall()

    close_mysql(conn, cur)

    return records
########################################### 从数据库中获取股票列表数据 #################################################
def get_stock_index_list_from_mysql(source_index_list_table_name):
    conn, cur = open_mysql()

    stock_list = []
    cur.execute("SELECT distinct stock_index  FROM %s" % source_index_list_table_name)
    records = cur.fetchall()
    for row in records:
        stock_list.append("%06d" %int(row[0]))

    print("Total Stock Number:%s  Time%s" %(len(records),(str(datetime.datetime.now()))))

    close_mysql(conn, cur)

    return stock_list

######################################### 通过Index从数据库中获取股票数据 ##############################################
def get_stock_recorde_by_index_from_mysql(source_index_list_table_name, stock_index):
    conn, cur = open_mysql()

    stock_list = []
    sqli = "SELECT * FROM {0} WHERE stock_index= '{1}'"
    sqli = sqli.format(source_index_list_table_name, stock_index)
    cur.execute(sqli)
    records = cur.fetchall()
    for row in records:
        stock_list.append("%06d" %int(row[0]))

    print("Total Stock Number:%s  Time%s" %(len(records),(str(datetime.datetime.now()))))

    close_mysql(conn, cur)

    return stock_list


########################################### 转换通达信数据并插入数据库 #################################################
def process_convert_tdx_to_mysql(stock_dir, mysql_table_name, stock_file_name, index, list_len):
    conn, cur = open_mysql()

    stock_file_path_name = stock_dir + stock_file_name
    stock_index = stock_file_name[3:9]
    stock_file = open( stock_file_path_name, "r", encoding='gbk', newline='')
    lines = stock_file.readlines()  # 读取全部内容
    #打印进度 时间 ID
    print("processed: %s%%,  Id:%s,  Time:%s" % (int((index / list_len) * 100), stock_index, (str(datetime.datetime.now()))))

    for line in lines:
        sqli = "insert into {0} values ('{1}',\"{2}\",{3},{4},{5},{6},{7},{8});"
        line = line.strip("\r\n")
        res= line.split('\t')
        if len(res) == 7  :
            sqlm = sqli.format(mysql_table_name, str(stock_index), res[0], res[1], res[2], res[3], res[4], res[5], res[6])
            try:
                cur.execute(sqlm)
                #print(sqlm)
            except:
                print("Insert Error", sqlm)

    conn.commit()
    close_mysql(conn, cur)

##################################### 启动多进程任务转换通达信数据并插入数据库 #########################################
def multi_process_convert_tdx_to_mysql(stock_dir, mysql_table_name):
    # 获取所有股票源文件列表
    stock_file_list = os.listdir(stock_dir)
    #启动多进程
    multi_process_job(process_convert_tdx_to_mysql,stock_file_list, args=(stock_dir,mysql_table_name))


########################################################################################################################
########################################        MACD 计算        #######################################################
########################################################################################################################
def my_round(number):
    # 设置精度取两位小数
    return round(number+0.0001,2)
################################################### 计算MACD 值 ########################################################
def calculate_macd(records, SHORT = 12, LONG =26, M = 9 ):
    macd_list = []
    index = 0
    precision = 2
    laset_row = None

    for row in records:
        code, date, open, high, low, close, volume, turnover = row[:8]
        index = index + 1
        if (index == 1):
            ema12 = close
            ema26 = close
            diff  = 0.0
            dea   = 0.0
            bar   = 0.0
            laset_row = row + (round(ema12, precision), round(ema26, precision), round(diff, precision), round(dea, precision), round(bar, precision),)
            macd_list.append(laset_row)
        else:
            ema12 = close*2/(SHORT + 1) + last_day_ema12*(SHORT - 1)/(SHORT + 1)
            ema26 = close*2/(LONG + 1)  + last_day_ema26*(LONG -1)/(LONG + 1)
            ema12 = my_round(ema12)
            ema26 = my_round(ema26)
            diff  = ema12 - ema26
            dea   = ((last_day_dea * 8) + (diff * 2))/10
            bar   = 2*(diff - dea)

            laset_row = row + (my_round(ema12), my_round(ema26), my_round(diff), my_round(dea), my_round(bar))
            macd_list.append(laset_row)
        last_day_ema12 = ema12
        last_day_ema26 = ema26
        last_day_dea = dea

    return macd_list

########################################################################################################################
#########################################        MA 计算        ########################################################
########################################################################################################################
################################################## 计算一组算术 MA 值 ##################################################
def calculate_ma(records, ma_x):
    queue_close = []
    ma_list = []
    index = 0
    for row in records:
        code, date, open, high, low, close, volume,turnover = row[:8]
        index = index + 1
        queue_close.append(float(close))
        ma_update = sum(queue_close)/len(queue_close)
        if(index >= ma_x ):
            queue_close.pop(0)
        ma_list.append(row +  (str(round(ma_update,2)),))
    return ma_list
######################################### 计算单只股票的算术MA 值 并插入数据库 #########################################
def process_calculat_ma_macd_to_mysql(from_table_name, to_talbe_name, stock_index, index, list_len):
    conn, cur = open_mysql()

    ma_list = [2, 3, 5, 8, 10, 13, 20, 21, 30, 34, 55, 60, 89, 120]

    # 打印进度 时间 ID
    print("processed: %s%%,  Id:%s,  Time:%s" % (
    int((index / list_len) * 100), stock_index, (str(datetime.datetime.now()))))

    sql = "SELECT * FROM {0} where stock_index = '{1}'"
    sql = sql.format(from_table_name,stock_index)
    cur.execute(sql)
    records = cur.fetchall()
    #计算MA
    for m_ma in ma_list:
        records = calculate_ma(records, m_ma)
    #计算MACD
    records = calculate_macd(records)
    for record in records:
        sqli = "insert into %s " %to_talbe_name + "values ('{0}',\"{1}\",{2},{3},{4},{5},{6},{7},{8},{9}," \
               "{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20});"
        code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, ma8, \
        ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = record[:27]
        sqlm = sqli.format(code, date, ma2, ma3, ma5, ma8, ma10, ma13, ma20, ma21, ma30,
                           ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar)
        # print(sqlm)
        try:
            cur.execute(sqlm)
            #print(sqlm)
        except:
            print("Insert Error", sqlm)

    conn.commit()
    close_mysql(conn, cur)

##################################### 启动多进程任务转换通达信数据并插入数据库 #########################################
def multi_process_calculat_ma_macd_to_mysql(from_table_name, to_talbe_name):
    #获取所有股票列表
    stock_list = get_stock_index_list_from_mysql(from_table_name)

    # 启动多进程
    multi_process_job(process_calculat_ma_macd_to_mysql, stock_list, args=(from_table_name, to_talbe_name))


####################################### 从拔地兔获取股票详细数据插入数据库 #############################################
def init_stock_detail_info_to_mysql(source_index_list_table_name, to_table_name):
    stock_list = get_stock_index_list_from_mysql(source_index_list_table_name)

    conn, cur = open_mysql()
    df_industry = ts.get_industry_classified()
    df_concept = ts.get_concept_classified()

    index = 0
    #print(len(df_industry.iterrows()))
    #print(len(df_concept.iterrows()))
    for stock_index in stock_list:
        concept = []       #所属概念
        index = index + 1
        stock_name = ""    #股票名称
        industry = ""      #所属行业
        for row in df_industry.iterrows():
            value= row[1]
            code = value[0]
            name = value[1]
            c_name = value[2]
            if(stock_index == code):
                stock_name = name
                industry   = c_name
                break

        for row in df_concept.iterrows():
            value = row[1]
            code = value[0]
            name = value[1]
            c_name = value[2]
            if(stock_index == code):
                if(len(stock_name)<2):
                    stock_name = name
                concept.append(c_name)
        if (len(stock_name) < 2):
            df = ts.get_realtime_quotes(stock_index)
            stock_name = str(df['name'].values[0])
        sqli = "insert into {0} values ('{1}','{2}','{3}','{4}');"
        sqlm = sqli.format(to_table_name, stock_index, stock_name, industry, ",".join(concept))
        print(index, sqlm)
        if(len(stock_name)>2):
            try:
                cur.execute(sqlm)
                conn.commit()
                # print(sqlm)
            except Exception as e:
                print("Insert DB Error", e, sqlm)
        else:
            print("Parameter Error: %s" %sqlm)

    close_mysql(conn, cur)

import pandas as pd
from pandas.compat import StringIO
import csv
def init_stock_basic_info_to_mysql(source_index_list_table_name, to_table_name):

    df_basic = ts.get_stock_basics()

    conn, cur = open_mysql()

    for stock_index,stock_basic in df_basic.iterrows():
        name, industry, area, pe, outstanding, totals, totalAssets, liquidAssets, fixedAssets, reserved, \
        reservedPerShare, esp, bvps, pb, timeToMarket, undp, perundp, rev, profit, gpr, npr,  holders = stock_basic[:22]

        sqli = "insert into {0} values ('{1}','{2}','{3}','{4}',{5},{6},{7},{8},{9}," \
               "{10},{11},{12},{13},{14},{15},\"{16}\",{17},{18},{19},{20},{21},{22},{23});"
        sqlm = sqli.format(to_table_name, stock_index, name, industry, area, my_round(pe), my_round(outstanding), my_round(totals),
                           my_round(totalAssets), my_round(liquidAssets), my_round(fixedAssets), my_round(reserved), my_round(reservedPerShare),
                           my_round(esp), my_round(bvps), my_round(pb), timeToMarket, my_round(undp), my_round(perundp),
                           my_round(rev), my_round(profit), my_round(gpr), my_round(npr),  my_round(holders))
        try:
            cur.execute(sqlm)

            # print(sqlm)
        except Exception as e:
            print("Insert DB Error", e, sqlm)

    conn.commit()
    close_mysql(conn, cur)


def test():
    m_dict = {"sum0": 0, "sum2": 0, "sum3": 0, "sum5": 0, "sum8": 0, "sum10": 0,"sum13": 0,
            "sum20": 0,"sum21": 0,  "sum30": 0,"sum34": 0,"sum55": 0,"sum60": 0,"sum89": 0,"sum120": 0}


    # 获取所有股票列表
    stock_list = get_stock_index_list_from_mysql('stock_raw_data')

    conn, cur = open_mysql()
    sql = "SELECT * FROM stock_ma_rate where stock_index = '{0}'  order by profit_rate desc limit 2;"
    lost = 0

    for stock_index in stock_list:
        sqli = sql.format(stock_index)
        cur.execute(sqli)
        records = cur.fetchall()
        #print(re[0][3])
        if(len(records)>0):
            for row in records:
                if(float(row[1])<0):
                    lost = lost + 1
                    print(stock_index, row[1], row[3])
                key = "sum%s" %row[3]
                m_dict[key]  = m_dict[key]  + 1

    print(m_dict)
    print(lost)

    close_mysql(conn, cur)

if __name__ == '__main__':

    starttime = datetime.datetime.now()
    print('Start time is %s.' % (str(datetime.datetime.now())))

    # 使用多进程转化通达信普通股票数据插入数据库
    multi_process_convert_tdx_to_mysql("d:\\Stock_Data\\", 'stock_raw_data')
    # 使用多进程计算普通股票MA/MACD数据并插入数据库
    multi_process_calculat_ma_macd_to_mysql('stock_raw_data','stock_ma_macd' )


    # 使用多进程转化通达信指数及基金数据插入数据库
    #multi_process_convert_tdx_to_mysql("d:\\Stock_Data\\", 'stock_index_raw_data')
    # 使用多进程计算指数及基金MA数据并插入数据库
    #multi_process_calculat_ma_to_mysql('stock_index_raw_data','stock_index_ma' )

    #获取股票名称 及 所属行业 概念等
    #init_stock_detail_info_to_mysql('stock_raw_data', 'stock_detail')
    #init_stock_basic_info_to_mysql('stock_raw_data', 'stock_basic')

    #test()

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))