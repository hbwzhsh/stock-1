
import os
import urllib
from urllib.request import *
import urllib.request
import re
import jieba
from util.operate_mysql import *
from util.operate_mysql import clear_table as clear_table
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
symbol_re  = re.compile("[\s+\.\\\!\/_,$^()<>=;%\"\']+|[—— ！，。？、~@#￥……&（）]", re.I)

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
        word_list.append(text)
    return word_list

def get_content_from_url():
    # 解析链接List，获取每个链接
    urls = []
    contents_list = []
    for index in range(1, 2):
        urls.extend(parase_url_from_list("http://blog.sina.com.cn/s/articlelist_1216826604_0_%s.html" % index))
    # print(urls)
    # 解析每个链接，获取文本内容
    for url in urls:
        contents_list.extend(parase_url_content(url))

    #保存文本到文件
    save_file = open("d:\\content.txt", "w")
    save_file.write(str(contents_list))
    save_file.close()

    return contents_list

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
    file_object = open(os.getcwd()+ '\\..\\script\\stock_dict.txt', 'r')
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

def get_contents_from_file():
    #保存文本到文件
    content_file = open("d:\\content.txt", "r")
    contentss = content_file.read()
    content_file.close()
    contents_list = contentss.split(',')
    return contents_list

def test_spider():
    clear_table('words_temp')  # 清除数据
    operatMySQl = OperateMySQL()

    # 生成分词字典
    if 0:
        generat_user_dict_into_db()
        generat_user_dict_from_db()


    jieba.load_userdict("d:\\userdict.txt")

    # 获取文本内容
    #contents_list = get_content_from_url()
    contents_list = get_contents_from_file()

    # 分词
    words_list = []
    for text in contents_list:
        splits = jieba.cut(text)
        for word in splits:
            words_list.append(word)

    # 统计分词频率，计入数据库
    counter = collections.Counter(words_list)
    '''
    for collect in counter:
        # print(collect,counter[collect])
        sqli = "insert into words_temp values ('{0}',{1});"
        sqlm = sqli.format(collect, counter[collect])
        # print(sqlm)
        operatMySQl.execute(sqlm)
    operatMySQl.commit()
    '''

    #判断你是否为股票名称
    for collect in counter:
        record = get_stock_basic_by_name(operatMySQl, collect)
        if record is not None and len(record) >0:
            #print(collect, counter[collect])
            sqli = "insert into words_temp values ('{0}',{1});"
            sqlm = sqli.format(collect, counter[collect])
            operatMySQl.execute(sqlm)
    operatMySQl.commit()

    # 清洗无用数据
    clean_date_table = ['的', '股', '是', '了', '我', '有', '也', '点', '在', '按',
                   ':', '-',
                   'NBSPWBR', 'LTLTSPANATITLEHREFHTTP', 'FONTASPANGTGT', 'SPAN', 'SPANSPANSPAN',
                   'LTLTSPANSTRONGATITLEHREFHTTP', 'ASTRONGSPANGTGT', 'NBSPWBRAHREFHTTP']
    for clean_item in clean_date_table:
        sqli = "delete from words_temp  where words_content = '{0}';"
        sqlm = sqli.format(clean_item)
        operatMySQl.execute(sqlm)
    operatMySQl.commit()
    # '''
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

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    print('Start time is %s.' % (str(datetime.datetime.now())))

    test_spider()

    # 程序结束时间 及 耗时
    timedelta = datetime.datetime.now() - starttime
    print('End time is %s.' % (str(datetime.datetime.now())))
    print('Total test execution duration is %s.' % (timedelta.__str__()))



