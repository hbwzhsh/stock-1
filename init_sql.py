#!/usr/bin/env python3
# -*- coding: utf-8 -*-
' init mysql database module '
__author__ = 'Yuechen Yang'

import pymysql
import os
import datetime
import tushare as ts
import csv
import multiprocessing
from decimal import *
from util.operate_mysql import *
from util.common import *
from util import vars as vs
from util.multi_processes import *
from stock_rule.covert_tdx_2_mysql import *
from stock_rule.calculat_ma_macd_2_mysql import *



####################################### 从拔地兔获取股票详细数据插入数据库 #############################################
def init_stock_detail_info_to_mysql(source_index_list_table_name, to_table_name):
    stock_list = get_stock_index_list_from_mysql(source_index_list_table_name)

    operatMySQl = OperateMySQL()

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
                operatMySQl.execute(sqlm)
                operatMySQl.commit()
                # print(sqlm)
            except Exception as e:
                print("Insert DB Error", e, sqlm)
        else:
            print("Parameter Error: %s" %sqlm)


def init_stock_basic_info_to_mysql(source_index_list_table_name, to_table_name):
    operatMySQl = OperateMySQL()

    df_basic = ts.get_stock_basics()
    #df_industry = ts.get_industry_classified()
    df_concept = ts.get_concept_classified()

    for stock_index,stock_basic in df_basic.iterrows():
        name, industry, area, pe, outstanding, totals, totalAssets, liquidAssets, fixedAssets, reserved, \
        reservedPerShare, esp, bvps, pb, timeToMarket, undp, perundp, rev, profit, gpr, npr,  holders = stock_basic[:22]

        concept = []  # 所属概念
        for row in df_concept.iterrows():
            value = row[1]
            code = value[0]
            c_name = value[2]
            if (stock_index == code):
                concept.append(c_name)

        sqli = "insert into {0} values ('{1}','{2}','{3}','{4}',{5},{6},{7},{8},{9}," \
               "{10},{11},{12},{13},{14},{15},\"{16}\",{17},{18},{19},{20},{21},{22},{23},'{24}');"
        sqlm = sqli.format(to_table_name, stock_index, name, industry, area, my_round(pe), my_round(outstanding), my_round(totals),
                           my_round(totalAssets), my_round(liquidAssets), my_round(fixedAssets), my_round(reserved), my_round(reservedPerShare),
                           my_round(esp), my_round(bvps), my_round(pb), timeToMarket, my_round(undp), my_round(perundp),
                           my_round(rev), my_round(profit), my_round(gpr), my_round(npr),  my_round(holders), ",".join(concept))
        try:
            operatMySQl.execute(sqlm)

            print(sqlm)
        except Exception as e:
            print("Insert DB Error", e, sqlm)

    operatMySQl.commit()



def test():
    m_dict = {"sum0": 0, "sum2": 0, "sum3": 0, "sum5": 0, "sum8": 0, "sum10": 0,"sum13": 0,
            "sum20": 0,"sum21": 0,  "sum30": 0,"sum34": 0,"sum55": 0,"sum60": 0,"sum89": 0,"sum120": 0}


    # 获取所有股票列表
    stock_list = get_stock_index_list_from_mysql('stock_raw_data')

    operatMySQl = OperateMySQL()

    sql = "SELECT * FROM stock_ma_rate where stock_index = '{0}'  order by profit_rate desc limit 2;"
    lost = 0

    for stock_index in stock_list:
        sqli = sql.format(stock_index)
        operatMySQl.execute(sqli)
        records = operatMySQl.fetchall()
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


if __name__ == '__main__':

    starttime = datetime.datetime.now()
    print('Start time is %s.' % (str(datetime.datetime.now())))

    '''
    init_database = Convert_TDX_2_Mysql(stock_dir ="d:\\Stock_Data\\",  mysql_table_name = 'stock_raw_data')
    calculat_ma_macd = Calculat_MA_MACD_2_Mysql( from_table_name = 'stock_raw_data', to_talbe_name = 'stock_ma_macd')

    clear_table('stock_raw_data')  # 清除数据
    # 使用多进程转化通达信普通股票数据插入数据库
    init_database.run_multi_process_job()

    clear_table('stock_ma_macd')  # 清除数据
    # 使用多进程计算普通股票MA/MACD数据并插入数据库
    calculat_ma_macd.run_multi_process_job()
    '''

    # 使用多进程转化通达信指数及基金数据插入数据库
    #multi_process_convert_tdx_to_mysql("d:\\Stock_Data\\", 'stock_index_raw_data')
    # 使用多进程计算指数及基金MA数据并插入数据库
    #multi_process_calculat_ma_to_mysql('stock_index_raw_data','stock_index_ma' )

    clear_table('stock_detail')  # 清除数据
    clear_table('stock_basic')  # 清除数据
    #获取股票名称 及 所属行业 概念等
    #init_stock_detail_info_to_mysql('stock_raw_data', 'stock_detail')
    init_stock_basic_info_to_mysql('stock_raw_data', 'stock_basic')

    #test()

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))