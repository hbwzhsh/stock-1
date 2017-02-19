#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' operating mysql module '

__author__ = 'Yuechen Yang'

from util import vars as vs
from util.dateu import *
import pymysql


class OperateMySQL(object):

    def __init__(self):
        try:
            self.__class__.conn = pymysql.connect(user=vs.MYSQL_USER_NAME, host=vs.MYSQL_HOST, passwd=vs.MYSQL_USER_PASSWD, db=vs.MYSQL_DB_NAME, charset=vs.MYSQL_CHARSET)
            self.__class__.cur = self.__class__.conn.cursor()
        except:
            print("Init mysql operater Error")
        finally:
            pass

        return

    def __del__(self):
        #'''
        try:
            #if self.__class__.cur is not None:
            self.__class__.cur.close()
                #self.__class__.cur = None
            #if self.__class__.conn is not None:
            self.__class__.conn.close()
                #self.__class__.conn = None
        except:
            print("Del mysql operater Error")
        finally:
            pass
        #'''
        return

    def get_operater(self):
        #if self.__class__.conn == None or self.__class__.cur == None:
        #    print("DB get operater error")
        return self.__class__.conn, self.__class__.cur

    def execute(self,sql):
        #if self.__class__.conn == None or self.__class__.cur == None:
        try:
            self.__class__.cur.execute(sql)
            # print(sqlm)
        except:
            print("Execute Error", sql)
        finally:
            pass
        return


    def fetchall(self):
        #if self.__class__.conn == None or self.__class__.cur == None:
        #    print("DB fetchall error")
        return  self.__class__.cur.fetchall()

    def commit(self):
        #if self.__class__.conn == None or self.__class__.cur == None:
        #    print("DB commit error")
        return  self.__class__.conn.commit()

############################################# 删除指定表中所有记录 #####################################################
def clear_table(clear_table_name):
    operatMySQl = OperateMySQL()

    sql = "TRUNCATE TABLE {0}"
    sql = sql.format(clear_table_name)
    # print(sql)
    operatMySQl.execute(sql)

    return


################################# 从数据库指定的表依据指定条件取出某支股票数据 #########################################
def get_stock_raw_data_from_mysql(stock_index, start_date, end_date, from_table):
    operatMySQl = OperateMySQL()

    sql = "SELECT *  FROM stock_raw_data natural join {0} where stock_index ='{1}' and (date>='{2}' and date <= '{3}')"
    sql = sql.format(from_table, stock_index, start_date, end_date)
    #print(sql)
    operatMySQl.execute(sql)
    records = operatMySQl.fetchall()

    return records

########################################### 从数据库中获取股票详细数据 #################################################
def get_stock_detail(stock_index):
    operatMySQl = OperateMySQL()

    sql = "SELECT *  FROM stock_detail where stock_index ='{0}';"
    sql = sql.format(stock_index)

    operatMySQl.execute(sql)
    records = operatMySQl.fetchall()

    return records

########################################### 从数据库中获取股票基本数据 #################################################
def get_stock_basic(stock_index):
    operatMySQl = OperateMySQL()

    sql = "SELECT *  FROM stock_basic where stock_index ='{0}';"
    sql = sql.format(stock_index)

    operatMySQl.execute(sql)
    records = operatMySQl.fetchall()

    stock_index, name, industry, area, pe, outstanding, totals, totalAssets, liquidAssets, fixedAssets, reserved,\
        reservedPerShare, esp, bvps, pb, timeToMarket, undp, perundp, rev, profit, gpr, npr, holders, = records[0][:23]
    info = "{0},{1:<5}, {2:<4}, 市盈率：{3}, 流通(亿)：{4} 总股本(亿)：{5}，每股公积金：{6}, 每股收益：{7} 每股净资：{8}，市净率：{9}， 上市日期：{10}， 每股未分配：{11}"
    info = info.format(stock_index, name, industry,pe, outstanding, totals,reservedPerShare,esp, bvps, pb,timeToMarket,perundp)
    return info

########################################### 从数据库中获取股票列表数据 #################################################
def get_stock_ma_macd_data_from_mysql(stock_index, start_date, end_date, from_table):
    operatMySQl = OperateMySQL()

    sql = "SELECT *  FROM stock_ma_macd where stock_index ='{1}' and (date>='{2}' and date <= '{3}')"
    sql = sql.format(from_table, stock_index, start_date, end_date)
    # print(sql)
    operatMySQl.execute(sql)
    records = operatMySQl.fetchall()

    return records



########################################### 从数据库中获取股票列表数据 #################################################
def get_stock_index_list_from_mysql(source_index_list_table_name):
    operatMySQl = OperateMySQL()

    stock_list = []
    operatMySQl.execute("SELECT distinct stock_index  FROM %s" % source_index_list_table_name)
    records = operatMySQl.fetchall()
    for row in records:
        stock_list.append("%06d" %int(row[0]))

    print("Total Stock Number:%s  Time%s" %(len(records),(str(datetime.datetime.now()))))

    return stock_list

######################################### 通过Index从数据库中获取股票数据 ##############################################
def get_stock_recorde_by_index_from_mysql(source_index_list_table_name, stock_index):
    operatMySQl = OperateMySQL()

    stock_list = []
    sqli = "SELECT * FROM {0} WHERE stock_index= '{1}'"
    sqli = sqli.format(source_index_list_table_name, stock_index)
    operatMySQl.execute(sqli)
    records = operatMySQl.fetchall()
    for row in records:
        stock_list.append("%06d" %int(row[0]))

    print("Total Stock Number:%s  Time%s" %(len(records),(str(datetime.datetime.now()))))

    return stock_list