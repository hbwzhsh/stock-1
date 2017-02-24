
from util.operate_mysql import *
from urllib.request import *
from util.common import *
import pandas as pd
import numpy as np
import pandas as pd

def init_sql_by_excel():
    clear_table('stock_deal')
    operatMySQl = OperateMySQL()
    path = u"D:\\s_data\\"
    #遍历目录所有文件
    s_data_list = os.listdir(path)
    for list_index in s_data_list:
        #读取交割单
        content_file = open(path+list_index, "r")
        contentss = content_file.read()
        content_file.close()
        contents_list = contentss.split('\n')
        index = 0
        for content_item in contents_list:
            #忽略第一行，表单头
            if index ==0 :
                index = 1
                continue

            line_list = content_item.split(',')
            #深市代码补全0
            if len(line_list[0])>0 and int(line_list[0])>0 and int(line_list[0])<4000 :
                line_list[0] = '%06d' %int(line_list[0])

            if(len(line_list)>10):
                sqli = "insert into stock_deal values ('{0[0]}','{0[1]}','{0[2]}',{0[3]},{0[4]},{0[5]},{0[6]},{0[7]},{0[8]}," \
                       "{0[9]},{0[10]},{0[11]},'{0[12]}','{0[13]}',\"{0[14]}\",{0[15]},{0[16]},{0[17]},'{0[18]}');"
                sqlm = sqli.format(line_list)
                #print(sqlm)
                operatMySQl.execute(sqlm)
    operatMySQl.commit()

#查询转入账户的金额之和
def query_amount_transferred_into_account():
    operatMySQl = OperateMySQL()
    conn, cur = operatMySQl.get_operater()
    sqlin ="SELECT * FROM  stock_deal where deal_type = '银行转证券'"
    df_in = pd.read_sql(sqlin, conn)
    print("转入：%s笔， 共" %len(df_in), sum(df_in['real_money']))
    sqlout ="SELECT * FROM  stock_deal where deal_type = '证券转银行'"
    df_out = pd.read_sql(sqlout, conn)
    print("转出：%s笔， 共" %len(df_out),sum(df_out['real_money']))

    print("账户：", sum(df_in['real_money'])+sum(df_out['real_money']))

    sqlInterest ="SELECT * FROM  stock_deal where deal_type = '利息归本'"
    df_sqlInterest = pd.read_sql(sqlInterest, conn)
    print("利息：%s笔， 共" %len(df_sqlInterest),sum(df_sqlInterest['real_money']))

def query_reverse_repo():
    operatMySQl = OperateMySQL()
    conn, cur = operatMySQl.get_operater()
    sqlsh = "SELECT * FROM  stock_deal where stock_index = '204001'"
    df_sh = pd.read_sql(sqlsh, conn)
    print("沪市1日：%s笔， 共" % len(df_sh), sum(df_sh['real_money']))

    sqlsz = "SELECT * FROM  stock_deal where stock_index = '131810'"
    df_sz = pd.read_sql(sqlsz, conn)
    print("深市1日：%s笔， 共" % len(df_sz), sum(df_sz['real_money']))

    sqlttl = "SELECT * FROM  stock_deal where stock_index = '205001'"
    df_ttl = pd.read_sql(sqlttl, conn)
    print("天天1日：%s笔， 共" % len(df_ttl), sum(df_ttl['real_money']))

    print("共计：%s笔， 共" %(len(df_sh)+len(df_sz)+len(df_ttl)),sum(df_sh['real_money'])+sum(df_sz['real_money'])+sum(df_ttl['real_money']))

def query_stock():
    operatMySQl = OperateMySQL()
    conn, cur = operatMySQl.get_operater()
    sqlsh = "SELECT * FROM  stock_deal where stock_index > '600000' and stock_index < '700000'"
    df_sh = pd.read_sql(sqlsh, conn)
    print("沪市：{0}笔， 共：{1}, 手续费：{2}，印花税：{3}".format(len(df_sh),
                                                   my_round(sum(df_sh['real_money'])),my_round(sum(df_sh['fees'])),
                                                   my_round(sum(df_sh['stamp_duty']))))

    sqlsz = "SELECT * FROM  stock_deal where stock_index > '000000' and stock_index < '100000'"
    df_sz = pd.read_sql(sqlsz, conn)
    print("深市：{0}笔， 共：{1}, 手续费：{2}，印花税：{3}".format(len(df_sz),
                                                   my_round(sum(df_sz['real_money'])), my_round(sum(df_sz['fees'])),
                                                   my_round(sum(df_sz['stamp_duty']))))


    sqlcy = "SELECT * FROM  stock_deal where stock_index > '300000' and stock_index < '400000'"
    df_cy = pd.read_sql(sqlcy, conn)
    print("创业：{0}笔， 共：{1}, 手续费：{2}，印花税：{3}".format(len(df_cy),
                                                   my_round(sum(df_cy['real_money'])), my_round(sum(df_cy['fees'])),
                                                   my_round(sum(df_cy['stamp_duty']))))

    print("合计：{0}笔， 共：{1}, 手续费：{2}，印花税：{3}".format(len(df_sh)+len(df_sz)+len(df_cy),
                                                   my_round(sum(df_sh['real_money'])+sum(df_sz['real_money'])+sum(df_cy['real_money'])),
                                                   my_round(sum(df_sh['fees'])+sum(df_sz['fees'])+sum(df_cy['fees'])),
                                                   my_round(sum(df_sh['stamp_duty']) + sum(df_sz['stamp_duty']) + sum(df_cy['stamp_duty']))))

if __name__ == '__main__':


    #init_sql_by_excel()
    #query_amount_transferred_into_account()
    #query_reverse_repo()
    query_stock()

