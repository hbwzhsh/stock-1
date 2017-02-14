#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' operating mysql module '

__author__ = 'Yuechen Yang'

from util import vars as vs
from util.dateu import *
import pymysql


class OperateMySQL(object):
    #conn = None
    #cur  = None

    def __init__(self):
        self.__class__.conn = pymysql.connect(user=vs.MYSQL_USER_NAME, host=vs.MYSQL_HOST, passwd=vs.MYSQL_USER_PASSWD, db=vs.MYSQL_DB_NAME, charset=vs.MYSQL_CHARSET)
        self.__class__.cur = self.__class__.conn.cursor()

    def __del__(self):
        if self.__class__.cur:
            self.__class__.cur.close()
            self.__class__.cur = None
        if self.__class__.conn:
            self.__class__.conn.close()
            self.__class__.conn = None

    def get_operater(self):
        #if self.__class__.conn == None or self.__class__.cur == None:
        #    print("DB get operater error")
        return self.__class__.conn, self.__class__.cur

    def execute(self,sql):
        # print(sql)
        #if self.__class__.conn == None or self.__class__.cur == None:
        #    print("DB execute error")
        self.__class__.cur.execute(sql)

    def fetchall(self):
        #if self.__class__.conn == None or self.__class__.cur == None:
        #    print("DB fetchall error")
        return  self.__class__.cur.fetchall()

    def commit(self):
        #if self.__class__.conn == None or self.__class__.cur == None:
        #    print("DB commit error")
        return  self.__class__.conn.commit()


################################# 从数据库指定的表依据指定条件取出某支股票数据 #########################################
def get_stock_raw_data_from_mysql(stock_index, start_date, end_date, from_table):
    operatMySQl = OperateMySQL()

    sql = "SELECT *  FROM stock_raw_data natural join {0} where stock_index ='{1}' and (date>='{2}' and date <= '{3}')"
    sql = sql.format(from_table, stock_index, start_date, end_date)
    #print(sql)
    operatMySQl.execute(sql)
    records = operatMySQl.fetchall()

    return records