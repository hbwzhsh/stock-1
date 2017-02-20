#!/usr/bin/env python3
# -*- coding: utf-8 -*-
' dig stock model '
__author__ = 'Yuechen Yang'
from util.operate_mysql import *
from util import vars as vs

from util.multi_processes import *
from util.process_job import *
from stock_rule.covert_tdx_2_mysql import *
from stock_rule.calculat_ma_macd_2_mysql import *
from stock_rule.dig_stock_by_nigh_times import *
from stock_rule.dig_stock_by_macd_low_deviation import *
from util.operate_mysql import *


if __name__ == '__main__':
    start_date_list = []
    end_date_list   = []

    testMultiprocess = Multi_Processes()
    starttime = datetime.datetime.now()
    print('Start time is %s.' % (str(datetime.datetime.now())))

    start_date_list.append('2016-12-1')  # 起始日期
    today = datetime.date.today().strftime("%Y-%m-%d")
    end_date_list.append(today)  # 结束日期

    from_table = 'stock_ma_macd'  # 数据源
    to_table   = 'stock_ma_rate'  # 目标表

    for (start_date, end_date) in zip(start_date_list, end_date_list):
        # 挖掘九转出低九
        Dig_Stock_By_Nigh_Times(start_date, end_date, from_table, to_table)

        # 挖掘MACD底背离
        #Dig_Stock_By_Macd_Low_Deviation(start_date, end_date, from_table, to_table).run_multi_process_job()

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))

