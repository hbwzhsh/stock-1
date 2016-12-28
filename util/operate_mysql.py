# -*- coding:utf-8 -*-

from util import vars as vs
import pymysql

def open_mysql():
    conn = pymysql.connect(user=vs.MYSQL_USER_NAME, host=vs.MYSQL_HOST, passwd=vs.MYSQL_USER_PASSWD, db=vs.MYSQL_DB_NAME, charset=vs.MYSQL_CHARSET)
    cur = conn.cursor()

    return conn, cur

    
def close_mysql(conn, cur):
    if cur and conn:
        cur.close()
        conn.close()
