from util.operate_mysql import *
from util import vars as vs

from util.multi_processes import *
from util.process_job import *
from stock_rule.covert_tdx_2_mysql import *
from stock_rule.calculat_ma_macd_2_mysql import *

from util.operate_mysql import *


if __name__ == '__main__':
    testMultiprocess = Multi_Processes()
    init_database = Convert_TDX_2_Mysql()
    calculat_ma_macd = Calculat_MA_MACD_2_Mysql()

    # 使用多进程转化通达信普通股票数据插入数据库
    #testMultiprocess.start_multi_process_job(init_database)

    # 使用多进程计算普通股票MA/MACD数据并插入数据库
    testMultiprocess.start_multi_process_job(calculat_ma_macd)