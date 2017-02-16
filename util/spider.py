

import urllib
from urllib.request import *
import urllib.request
import re

urlre = re.compile(r'(http://[^/\\]+)', re.I)
hrefre = re.compile(r'<a href=".*?<\/a>', re.I)
blogre = re.compile(r'http://blog.sina.com.cn/[\w]+[/\d]*', re.I)
title_re = re.compile(r'>(.*)</a>', re.I)
filterre = re.compile(r'.htm?|.xml|</p>|http://blog.sina.com.cn/[\w]+/[\w]+/', re.I)
log_url_re = re.compile(r'<a title=\"\" target=\"_blank\" href=".*?<\/a>', re.I)

title_zb = re.compile(r'(.*)wu2198股市直播', re.I)
content_re = re.compile(r'<p>(.*)\w+:\d\d([\w\W]*?)<\/p>', re.I)

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
        if blogre.match(url) is not None and title is not None:
            urllist.append((url, title))

    for url in urllist:
        print(url)

def parase_url_content(url):
    filehandle = urllib.request.urlopen(url)
    content = filehandle.read()  # read
    #content = content.replace('\r\n','')
    content = content.decode('utf-8') # python3

    content_list = content_re.findall(content)
    '''
    content_re1 = re.compile(r'(.*)\d:\d(.*)', re.I)
    for item in content_list:
        if(content_re1.match(item)):
            print(item)
    '''
    for item in content_list:
        print(item[1].strip())

if __name__ == '__main__':
    parase_url_content('http://blog.sina.com.cn/s/blog_48874cec0102x4zm.html')
    #for index in range(1,3):
    #    parase_url_from_list("http://blog.sina.com.cn/s/articlelist_1216826604_0_%s.html" %index)
