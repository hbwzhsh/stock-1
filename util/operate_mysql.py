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
        if self.__class__.conn:
            self.__class__.conn.close()

    def get_operater(self):
        return self.__class__.conn, self.__class__.cur

    def execute(self,sql):
        # print(sql)
        self.__class__.cur.execute(sql)

    def fetchall(self):
        return  self.__class__.cur.fetchall()

    def commit(self):
        return  self.__class__.conn.commit()
