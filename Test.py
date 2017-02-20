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

def generat_user_dict_into_db():
    #更新股票字典数据库从股票基本数据
    clear_table('stock_dict')  # 清除数据
    operatMySQl = OperateMySQL()
    operatMySQl.execute("SELECT *  FROM stock_basic")
    records = operatMySQl.fetchall()
    for row in records:
        stock_index    = row[0]  #股票代码
        stock_name     = row[1]  #股票名称
        stock_industry = row[2]  #股票行业
        stock_concept  = row[23] #股票概念
        sqli = "insert into stock_dict values ('{0}');"
        sqlm = sqli.format(stock_index)
        operatMySQl.execute(sqlm)
        sqlm = sqli.format(stock_name)
        operatMySQl.execute(sqlm)
        sqlm = sqli.format(stock_industry)
        operatMySQl.execute(sqlm)
        concept_list= stock_concept.split(',')
        for concept in concept_list:
            sqlm = sqli.format(concept)
            operatMySQl.execute(sqlm)

    operatMySQl.commit()

    # 更新股票字典数据库从自定义字典文件
    file_object = open('d:\\stock_dict.txt', 'r')
    content = file_object.read() #.decode('utf-8')
    file_object.close()
    stock_list = content.split('\n')
    for stock_dict in stock_list:
        #print(stock_dict.strip())
        sqli = "insert into stock_dict values ('{0}');"
        sqlm = sqli.format(stock_dict.strip())
        operatMySQl.execute(sqlm)
    operatMySQl.commit()

    return

def generat_user_dict_from_db():
    operatMySQl = OperateMySQL()
    file_object = codecs.open('d:\\userdict.txt', 'w', "utf-8")

    operatMySQl.execute("SELECT *  FROM stock_dict")
    records = operatMySQl.fetchall()
    for row in records:
        stock_dict = row[0] + ' 1 nr\r\n'
        file_object.write(stock_dict)

    file_object.close()

    return

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
    test_login()
    #test_chelv()


