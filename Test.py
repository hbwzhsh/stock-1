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
import requests

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

def test_login():
    result = urllib.request.urlopen("http://www.scsjgjj.com/")
    soup = bs4.BeautifulSoup(result, "html.parser")

    logindiv = soup.find(attrs={'class','person_text'})
    p1 = soup.find(attrs={'id','ctl00_ContentPlaceHolder1_QueryFund1_txtUserName'})

    #logindiv.text = '90388886'
    print( p1['ctl00_ContentPlaceHolder1_QueryFund1_txtUserName'])
    #logindiv = soup.find("text", attrs={"name": "p1_search"})
    Allinput = logindiv.findAll("input")
    inputData = {}
    for oneinput in Allinput:
        if oneinput.has_attr('name'):
            if oneinput.has_attr('value'):
                inputData[oneinput['name']] = oneinput['value']
            else:
                inputData[oneinput['name']] = ""
    inputData['ctl00_ContentPlaceHolder1_QueryFund1_txtUserName'] = '90388886'
    #inputData['ctl00$ContentPlaceHolder1$txtUsername_Lib'] = '*******'
    print(logindiv.text)

    filename = 'cookie.txt'
    # 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
    cookie = http.cookiejar.CookieJar() #cookielib.MozillaCookieJar(filename)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
    postdata = urllib.urlencode(inputData)
    result2 = opener.open("http://www.scsjgjj.com/", postdata)
    cookie.save(ignore_discard=True, ignore_expires=True)
    # 登录后 要访问的url
    bookUrl = "http://222.200.122.171:7771/user/userinfo.aspx"
    result = opener.open(bookUrl)
    print(result.read())

def test_my_login():
    sessions = requests.session()

    login_data = {'BaseRate' : '1',
                'MaxMoney' : '70',
                'Ratel' : '2.75',
                'Ratel10' : '3.25',
                '__VIEWSTATEGENERATOR' : '90059987',
                'ctl00$ContentPlaceHolder1$QueryFund1$btnPost' : '提交',
                'ctl00$ContentPlaceHolder1$QueryFund1$txtUserName': '90388886',
                'ctl00$ContentPlaceHolder1$QueryFund1$txtPassword': '90388886',
                'ctl00$ContentPlaceHolder1$QueryFund1$txtCode': 'ABCD',
                'ctl00$ContentPlaceHolder1$Toupiao$diaocha' : 'RadioButton1',
                'discount1' : '30',
                'rdoType' : '1',
                'selRateYear' : '30'
                }
    header = {
        'Accept' : 'text / html, application / xhtml + xml, application / xml;q = 0.9, * / *;q = 0.8',
        'Accept - Encoding' : 'gzip, deflate',
        'Accept - Language' : 'zh - CN, zh;q = 0.8, en - US;q = 0.5, en;q = 0.3',

        'Host': 'www.scsjgjj.com',
        'Referer': 'http://www.scsjgjj.com/Index.aspx',
        'Connection': 'Keep-Alive',
        'Upgrade - Insecure - Requests' : '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'
    }
    # post登录
    r = sessions.post('http://www.scsjgjj.com/', data=login_data,headers=header)
    soup = bs4.BeautifulSoup(r.text)
    print(r)

if __name__ == '__main__':
    #generat_user_dict_into_db()
    #generat_user_dict_from_db()
    #test_login()
    #test_chelv()

    #join_excel()
    test_my_login()


