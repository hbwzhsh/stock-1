from stock_rule.back_test.back_test_calculat_stock_max_lose import *
from stock_rule.back_test.back_test_low_nigh_times import *
from stock_rule.back_test.back_test_stock_rate_macd_deviation import *
from stock_rule.dig_stock_by_macd_low_deviation import *
from stock_rule.dig_stock_by_nigh_times import *
from util.operate_mysql import *

import urllib
from urllib.request import *
import urllib.request
import re
import codecs
import urllib
import http.cookiejar
#import cookielib
import bs4
import pandas as pd
import numpy as np
import pandas as pd

def test_chelv():

    init_database = Convert_TDX_2_Mysql(stock_dir="d:\\Stock_Data\\", mysql_table_name='stock_raw_data')
    calculat_ma_macd = Calculat_MA_MACD_2_Mysql(from_table_name='stock_raw_data', to_talbe_name='stock_ma_macd')

    dig_stock_by_nig_times = Dig_Stock_By_Nigh_Times(start_date='2016-11-1',
                                                     end_date=datetime.date.today().strftime("%Y-%m-%d"),
                                                     from_table='stock_ma_macd',
                                                     to_table='stock_ma_rate')

    dig_stock_by_macd_low_deviation = Dig_Stock_By_Macd_Low_Deviation(start_date='2016-11-1',
                                                                      end_date=datetime.date.today().strftime("%Y-%m-%d"),
                                                                      from_table='stock_ma_macd',
                                                                      to_table='stock_ma_rate')

    back_test_max_lose = Back_Test_Calculat_Stock_Max_Lose(start_date='2016-6-1',
                                                           end_date=datetime.date.today().strftime("%Y-%m-%d"),
                                                           from_table='stock_ma_macd',
                                                           to_table='stock_temp_rate')

    back_test_low_nigh_times = Back_Test_Low_Nigh_Times(start_date='2015-6-1',
                                                        end_date=datetime.date.today().strftime("%Y-%m-%d"),
                                                        from_table='stock_ma_macd',
                                                        to_table='stock_win_rate')

    back_test_stock_rate_macd_deviation = Back_Test_Stock_Rate_Macd_Deviation(start_date='2015-6-1',
                                                                              end_date=datetime.date.today().strftime(
                                                                                  "%Y-%m-%d"),
                                                                              from_table='stock_ma_macd',
                                                                              to_table='stock_win_rate')

    # 使用多进程转化通达信普通股票数据插入数据库
    # init_database.run_multi_process_job()

    # 使用多进程计算普通股票MA/MACD数据并插入数据库
    # calculat_ma_macd.run_multi_process_job()

    # 挖掘九转出低九
    # dig_stock_by_nig_times.run_multi_process_job()

    # 挖掘MACD底背离
    # dig_stock_by_macd_low_deviation.run_multi_process_job()

    # 计算一段时间内最大跌幅
    # back_test_max_lose.run_multi_process_job()

    # 九转回测
    # back_test_low_nigh_times.run_multi_process_job()

    # MACD 底背离回测
    # back_test_stock_rate_macd_deviation.run_multi_process_job()

def join_excel():
    clear_table('stock_deal')
    operatMySQl = OperateMySQL()
    path = u"D:\\s_data\\"
    s_data_list = os.listdir(path)
    for list_index in s_data_list:
        content_file = open(path+list_index, "r")
        contentss = content_file.read()
        content_file.close()
        contents_list = contentss.split('\n')
        index = 0
        for content_item in contents_list:
            if index ==0 :
                index = 1
                continue


            sqli = "insert into stock_deal values ('{0[0]}','{0[1]}','{0[2]}',{0[3]},{0[4]},{0[5]},{0[6]},{0[7]},{0[8]}," \
                        "{0[9]},{0[10]},{0[11]},'{0[12]}','{0[13]}',\"{0[14]}\",{0[15]},{0[16]},{0[17]},'{0[18]}');"

            #sqli = "insert into stock_deal values ('{0[0]}','{0[1]}', '{0[20[}',{0[3]},{0[4]},{0[5]},{0[6]},{0[7]},{0[8]}," \
            #       "{0[9]},{0[10]},{0[11]},'{0[12]}','{0[13]}',\"{0[14]}\",{0[15]},{0[16]},{0[17]},'{0[18]}');"
            line_list = content_item.split(',')
            if len(line_list[0])>0 and int(line_list[0])>0 and int(line_list[0])<4000 :
                line_list[0] = '%06d' %int(line_list[0])

            if(len(line_list)>10):
                #print(line_list)
                sqlm = sqli.format(line_list)
                print(sqlm)
                operatMySQl.execute(sqlm)

    operatMySQl.commit()
        #print(contents_list)
        #df = pd.read_excel(path+list_index, encoding_override="utf-8")

def query_money():
    operatMySQl = OperateMySQL()
    conn, cur = operatMySQl.get_operater()

    sqli ="SELECT * FROM  stock_deal where deal_type = '银行转证券' or deal_type = '证券转银行'"
    df = pd.read_sql(sqli, conn)
    #print()
    print(sum(df['real_money']))
    #for index, item in df:
    #    print(index, item)
    '''
    operatMySQl.execute(sqli)
    records = operatMySQl.fetchall()
    for record in records:
        print(record)
    '''


def test_login():
    result = urllib.request.urlopen.urlopen("http://222.200.122.171:7771/login.aspx")
    soup = bs4.BeautifulSoup(result, "html.parser")

    logindiv = soup.find("form", attrs={"name": "aspnetForm"})
    Allinput = logindiv.findAll("input")
    inputData = {}
    for oneinput in Allinput:
        if oneinput.has_attr('name'):
            if oneinput.has_attr('value'):
                inputData[oneinput['name']] = oneinput['value']
            else:
                inputData[oneinput['name']] = ""
    inputData['ctl00$ContentPlaceHolder1$txtPas_Lib'] = '*****'
    inputData['ctl00$ContentPlaceHolder1$txtUsername_Lib'] = '*******'

    filename = 'cookie.txt'
    # 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
    cookie = http.cookiejar.CookieJar() #cookielib.MozillaCookieJar(filename)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
    postdata = urllib.urlencode(inputData)
    result2 = opener.open("http://222.200.122.171:7771/login.aspx", postdata)
    cookie.save(ignore_discard=True, ignore_expires=True)
    # 登录后 要访问的url
    bookUrl = "http://222.200.122.171:7771/user/userinfo.aspx"
    result = opener.open(bookUrl)
    print(result.read())

if __name__ == '__main__':
    #generat_user_dict_into_db()
    #generat_user_dict_from_db()
    #test_login()
    #test_chelv()

    #join_excel()
    query_money()


