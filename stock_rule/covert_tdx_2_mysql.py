#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' multi job module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
import os

class Convert_TDX_2_Mysql(Process_Job):

    def process(self,stock_dir, mysql_table_name, stock_file_name, index, list_len):
        operatMySQl = OperateMySQL()

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
                    operatMySQl.execute(sqlm)
                    #print(sqlm)
                except:
                    print("Insert Error", sqlm)

        operatMySQl.commit()

    def get_list(self):
        stock_dir =  "d:\\Stock_Data\\"
        return os.listdir(stock_dir)

    def get_args(self):
        stock_dir =  "d:\\Stock_Data\\"
        mysql_table_name = 'stock_raw_data'
        return stock_dir,mysql_table_name
