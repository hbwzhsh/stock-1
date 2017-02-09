#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' multi job module '

__author__ = 'Yuechen Yang'

from util.operate_mysql import *
from util.process_job import *
from util.common import *

class Calculat_MA_MACD_2_Mysql(Process_Job):

    ########################################### 从数据库中获取股票列表数据 #################################################
    def get_stock_index_list_from_mysql(self, source_index_list_table_name):
        operatMySQl = OperateMySQL()

        stock_list = []
        operatMySQl.execute("SELECT distinct stock_index  FROM %s" % source_index_list_table_name)
        records = operatMySQl.fetchall()
        for row in records:
            stock_list.append("%06d" % int(row[0]))

        print("Total Stock Number:%s  Time%s" % (len(records), (str(datetime.datetime.now()))))

        return stock_list

    ########################################################################################################################
    ########################################        MACD 计算        #######################################################
    ########################################################################################################################
    ################################################### 计算MACD 值 ########################################################
    def calculate_macd(self, records, SHORT=12, LONG=26, M=9):
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
                diff = 0.0
                dea = 0.0
                bar = 0.0
                laset_row = row + (
                round(ema12, precision), round(ema26, precision), round(diff, precision), round(dea, precision),
                round(bar, precision),)
                macd_list.append(laset_row)
            else:
                ema12 = close * 2 / (SHORT + 1) + last_day_ema12 * (SHORT - 1) / (SHORT + 1)
                ema26 = close * 2 / (LONG + 1) + last_day_ema26 * (LONG - 1) / (LONG + 1)
                ema12 = my_round(ema12)
                ema26 = my_round(ema26)
                diff = ema12 - ema26
                dea = ((last_day_dea * 8) + (diff * 2)) / 10
                bar = 2 * (diff - dea)

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
    def calculate_ma(self, records, ma_x):
        queue_close = []
        ma_list = []
        index = 0
        for row in records:
            code, date, open, high, low, close, volume, turnover = row[:8]
            index = index + 1
            queue_close.append(float(close))
            ma_update = sum(queue_close) / len(queue_close)
            if (index >= ma_x):
                queue_close.pop(0)
            ma_list.append(row + (str(round(ma_update, 2)),))
        return ma_list

    ######################################### 计算单只股票的算术MA 值 并插入数据库 #########################################
    def process(self, from_table_name, to_talbe_name, stock_index, index, list_len):
        operatMySQl = OperateMySQL()

        ma_list = [2, 3, 5, 8, 10, 13, 20, 21, 30, 34, 55, 60, 89, 120]

        # 打印进度 时间 ID
        print("processed: %s%%,  Id:%s,  Time:%s" % (
            int((index / list_len) * 100), stock_index, (str(datetime.datetime.now()))))

        sql = "SELECT * FROM {0} where stock_index = '{1}'"
        sql = sql.format(from_table_name, stock_index)
        operatMySQl.execute(sql)
        records = operatMySQl.fetchall()
        # 计算MA
        for m_ma in ma_list:
            records = self.calculate_ma(records, m_ma)
        # 计算MACD
        records = self.calculate_macd(records)
        for record in records:
            sqli = "insert into %s " % to_talbe_name + "values ('{0}',\"{1}\",{2},{3},{4},{5},{6},{7},{8},{9}," \
                                                       "{10},{11},{12},{13},{14},{15},{16},{17},{18},{19},{20});"
            code, date, open, high, low, close, volume, turnover, ma2, ma3, ma5, ma8, \
            ma10, ma13, ma20, ma21, ma30, ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar = record[:27]
            sqlm = sqli.format(code, date, ma2, ma3, ma5, ma8, ma10, ma13, ma20, ma21, ma30,
                               ma34, ma55, ma60, ma89, ma120, ema12, ema26, diff, dea, bar)
            # print(sqlm)
            try:
                operatMySQl.execute(sqlm)
                # print(sqlm)
            except:
                print("Insert Error", sqlm)

        operatMySQl.commit()


    def get_list(self):
        return self.get_stock_index_list_from_mysql('stock_raw_data')

    def get_args(self):
        from_table_name  = 'stock_raw_data'
        to_talbe_name    = 'stock_ma_macd'
        return from_table_name,to_talbe_name
