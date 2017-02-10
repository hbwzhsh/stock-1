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
    testMultiprocess = Multi_Processes()
    init_database = Convert_TDX_2_Mysql(stock_dir ="d:\\Stock_Data\\",  mysql_table_name = 'stock_raw_data')
    calculat_ma_macd = Calculat_MA_MACD_2_Mysql( from_table_name = 'stock_raw_data', to_talbe_name = 'stock_ma_macd')

    start_date = '2016-11-1'
    end_date = datetime.date.today().strftime("%Y-%m-%d")  # today
    from_table = 'stock_ma_macd'  # 数据源
    to_table = 'stock_ma_rate'  # 目标表
    dig_stock_by_nig_times = Dig_Stock_By_Nigh_Times(start_date, end_date, from_table, to_table)

    dig_stock_by_macd_low_eeviation = Dig_Stock_By_Macd_Low_Deviation(start_date, end_date, from_table, to_table)

    # 使用多进程转化通达信普通股票数据插入数据库
    #testMultiprocess.start_multi_process_job(init_database)

    # 使用多进程计算普通股票MA/MACD数据并插入数据库
    #testMultiprocess.start_multi_process_job(calculat_ma_macd)

    # 挖掘九转出低九
    #testMultiprocess.start_multi_process_job(dig_stock_by_nig_times)

    # 挖掘MACD底背离
    testMultiprocess.start_multi_process_job(dig_stock_by_macd_low_eeviation)