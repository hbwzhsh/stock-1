from stock_rule.back_test.back_test_calculat_stock_max_lose import *
from stock_rule.back_test.back_test_low_nigh_times import *
from stock_rule.back_test.back_test_stock_rate_macd_deviation import *
from stock_rule.dig_stock_by_macd_low_deviation import *
from stock_rule.dig_stock_by_nigh_times import *
from util.operate_mysql import *

if __name__ == '__main__':
    testMultiprocess = Multi_Processes()
    init_database = Convert_TDX_2_Mysql(stock_dir ="d:\\Stock_Data\\",  mysql_table_name = 'stock_raw_data')
    calculat_ma_macd = Calculat_MA_MACD_2_Mysql( from_table_name = 'stock_raw_data', to_talbe_name = 'stock_ma_macd')


    dig_stock_by_nig_times = Dig_Stock_By_Nigh_Times(start_date = '2016-11-1',
                                                            end_date = datetime.date.today().strftime("%Y-%m-%d"),
                                                            from_table = 'stock_ma_macd',
                                                            to_table ='stock_ma_rate')

    dig_stock_by_macd_low_deviation = Dig_Stock_By_Macd_Low_Deviation(start_date = '2016-11-1',
                                                            end_date = datetime.date.today().strftime("%Y-%m-%d"),
                                                            from_table = 'stock_ma_macd',
                                                            to_table ='stock_ma_rate')

    back_test_max_lose =  Back_Test_Calculat_Stock_Max_Lose(start_date = '2016-6-1',
                                                            end_date = datetime.date.today().strftime("%Y-%m-%d"),
                                                            from_table = 'stock_ma_macd',
                                                            to_table ='stock_temp_rate')

    back_test_low_nigh_times = Back_Test_Low_Nigh_Times(start_date='2015-6-1',
                                                           end_date=datetime.date.today().strftime("%Y-%m-%d"),
                                                           from_table='stock_ma_macd',
                                                           to_table='stock_win_rate')

    back_test_stock_rate_macd_deviation = Back_Test_Stock_Rate_Macd_Deviation(start_date='2015-6-1',
                                                           end_date=datetime.date.today().strftime("%Y-%m-%d"),
                                                           from_table='stock_ma_macd',
                                                           to_table='stock_win_rate')
    # 使用多进程转化通达信普通股票数据插入数据库
    #testMultiprocess.start_multi_process_job(init_database)

    # 使用多进程计算普通股票MA/MACD数据并插入数据库
    #testMultiprocess.start_multi_process_job(calculat_ma_macd)

    # 挖掘九转出低九
    #testMultiprocess.start_multi_process_job(dig_stock_by_nig_times)

    # 挖掘MACD底背离
    #testMultiprocess.start_multi_process_job(dig_stock_by_macd_low_deviation)

    # 计算一段时间内最大跌幅
    #testMultiprocess.start_multi_process_job(back_test_max_lose)

    # 九转回测
    #testMultiprocess.start_multi_process_job(back_test_low_nigh_times)
    
    #MACD 底背离回测
    testMultiprocess.start_multi_process_job(back_test_stock_rate_macd_deviation)