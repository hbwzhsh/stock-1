

import urllib
from urllib.request import *
import urllib.request
import re
import jieba
from util.operate_mysql import *
from multiprocessing.dummy import Pool as ThreadPool
import collections
import codecs

urlre = re.compile(r'(http://[^/\\]+)', re.I)
hrefre = re.compile(r'<a href=".*?<\/a>', re.I)
blogre = re.compile(r'http://blog.sina.com.cn/[\w]+[/\d]*', re.I)
title_re = re.compile(r'>(.*)</a>', re.I)
filterre = re.compile(r'.htm?|.xml|</p>|http://blog.sina.com.cn/[\w]+/[\w]+/', re.I)
log_url_re = re.compile(r'<a title=\"\" target=\"_blank\" href=".*?<\/a>', re.I)

title_zb   = re.compile(r'(.*)wu2198股市直播', re.I)
content_re = re.compile(r'<p>(.*)\w+:\d\d([\w\W]*?)<\/p>', re.I)
symbol_re  = re.compile("[\s+\.\!\/_,$%^()<>=;+\"\']+|[+——！，。？、~@#￥%……&（）]+", re.I)

def parase_url_from_list(url_list):
    '''
        parse all sinablog url from a assign html
        sinablog url include two rule:
        1)http://blog.sina.com.cn/xxxxx
        2)http://blog.sina.com.cn/x/xxxxxx

    '''
    # urlmatch = urlre.match(websize)
    urllist = []
    filehandle = urllib.request.urlopen(url_list)
    content = filehandle.read()  # read
    content = content.decode('utf-8')  # python3
    hrefs = log_url_re.findall(content)

    for href in hrefs:
        splits = href.split(' ')
        if len(splits) != 1:
            href = splits[3]
        # get text of href tag
        #title = title_re.findall(href)
        title = None
        if title_zb.match(href) is not None:
            title = title_re.findall(href)
        matches = re.match('href="(.*)"', href)
        if matches is not None:
            url = matches.group(1)
            #if blogre.match(url) is not None:
                #urllist.append((url, title))
        if blogre.match(url) is not None: # and title is not None:
            #urllist.append((url, title))
            #print((url, title))
            urllist.append(url)

    #for url in urllist:
    #    print(url)
    return urllist

def parase_url_content(url):
    filehandle = urllib.request.urlopen(url)
    content = filehandle.read()  # read
    content = content.decode('utf-8') # python3
    content_list = content_re.findall(content)

    word_list = []
    for item in content_list:
        text = symbol_re.sub(u'', item[1].strip()).upper()
        splits = jieba.cut(text)
        for word in splits:
            word_list.append(word)

    return word_list

def generat_user_dict():
    operatMySQl = OperateMySQL()
    file_object = codecs.open('d:\\userdict.txt', 'w', "utf-8")

    stock_list = []
    operatMySQl.execute("SELECT *  FROM stock_basic")
    records = operatMySQl.fetchall()
    for row in records:
        stock_list.append(row[0])
        stock_name = row[1] + ' 1 nr\r\n'
        #stock_name= stock_name + ' 1 nr\r\n'
        stock_industry = row[2] + ' 1 nr\r\n'
        file_object.write(stock_name)
        file_object.write(stock_industry)

    file_object.close()
    #print("Total Stock Number:%s  Time%s" %(len(records),(str(datetime.datetime.now()))))

    return stock_list

if __name__ == '__main__':
    generat_user_dict()
    #'''
    clear_table('words_temp')  # 清除数据
    jieba.load_userdict("d:\\userdict.txt")

    starttime = datetime.datetime.now()
    print('Start time is %s.' % (str(datetime.datetime.now())))
    #parase_url_content('http://blog.sina.com.cn/s/blog_48874cec0102x4zm.html')
    urls = []
    words_list = []
    for index in range(1,3):
        urls.extend(parase_url_from_list("http://blog.sina.com.cn/s/articlelist_1216826604_0_%s.html" %index))
    #print(urls)

    for url in urls:
        words_list.extend(parase_url_content(url))

    #print(collections.Counter(words_list))
    counter = collections.Counter(words_list)
    operatMySQl = OperateMySQL()
    for collect in counter:
        #print(collect,counter[collect])
        sqli = "insert into words_temp values ('{0}',{1});"
        sqlm = sqli.format(collect,counter[collect])
        # print(sqlm)
        operatMySQl.execute(sqlm)
    operatMySQl.commit()
    #'''
    '''
    # Make the Pool of workers
    pool = ThreadPool(4)
    # Open the urls in their own threads
    # and return the results
    results = pool.map(parase_url_content, urls)
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()
    '''

    '''
    text    =    '我来到北京清华大学'

    default_mode  =    jieba.cut(text)
    full_mode     =    jieba.cut(text, cut_all=True)
    search_mode   =    jieba.cut_for_search(text)


    print("精确模式:", "/".join(default_mode))
    print("全模式:", "/".join(full_mode))
    print("搜索引擎模式:", "/".join(search_mode))
    '''

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))



