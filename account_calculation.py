
from util.operate_mysql import *
from urllib.request import *
from util.common import *
import numpy as np
import pandas as pd
import os
from sqlalchemy import create_engine
import codecs

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
    sql_list = []
    sql_list.append(("沪市1日","SELECT * FROM  stock_deal where stock_index = '204001'"))
    sql_list.append(("深市1日","SELECT * FROM  stock_deal where stock_index = '131810'"))
    sql_list.append(("天天1日","SELECT * FROM  stock_deal where stock_index = '205001'"))
    sql_list.append(("共计", "SELECT * FROM  stock_deal where stock_index = '204001' or stock_index = '131810' or stock_index = '205001'"))
    for sql in sql_list:
        df = pd.read_sql(sql[1], conn)
        print("{0}：{1}笔， 共：{2}".format(sql[0], len(df),my_round(sum(df['real_money']))))

    '''
    sqlsh =
    df_sh = pd.read_sql(sqlsh, conn)
    print("沪市1日：%s笔， 共" % len(df_sh), sum(df_sh['real_money']))

    sqlsz = "SELECT * FROM  stock_deal where stock_index = '131810'"
    df_sz = pd.read_sql(sqlsz, conn)
    print("深市1日：%s笔， 共" % len(df_sz), sum(df_sz['real_money']))

    sqlttl = "SELECT * FROM  stock_deal where stock_index = '205001'"
    df_ttl = pd.read_sql(sqlttl, conn)
    print("天天1日：%s笔， 共" % len(df_ttl), sum(df_ttl['real_money']))

    print("共计：%s笔， 共" %(len(df_sh)+len(df_sz)+len(df_ttl)),sum(df_sh['real_money'])+sum(df_sz['real_money'])+sum(df_ttl['real_money']))
    '''
#查询手续费 印花税
def query_fees_stamp_duty():
    operatMySQl = OperateMySQL()
    conn, cur = operatMySQl.get_operater()

    sql_list = []
    sql_list.append(("沪市", "SELECT * FROM  stock_deal where stock_index > '600000' and stock_index < '700000'"))
    sql_list.append(("深市", "SELECT * FROM  stock_deal where stock_index > '000000' and stock_index < '100000'"))
    sql_list.append(("创业", "SELECT * FROM  stock_deal where stock_index > '300000' and stock_index < '400000'"))
    sql_list.append(("基金", "SELECT * FROM  stock_deal where stock_index > '150000' and stock_index < '200000'"))
    sql_list.append(("合计", "SELECT * FROM  stock_deal where "
    "((stock_index > '300000' and stock_index < '700000') or (stock_index > '150000' and stock_index < '200000') or (stock_index > '000000' and stock_index < '100000'))"))

    for sql in sql_list:
        df = pd.read_sql(sql[1], conn)
        print("{0}：{1}笔， 共：{2}, 手续费：{3}，印花税：{4}, 成交额：{5}".format(sql[0], len(df),
                                                       my_round(sum(df['real_money'])), my_round(sum(df['fees'])),
                                                       my_round(sum(df['stamp_duty'])), my_round(sum(df['deal_money']))))

def query_stock():
    operatMySQl = OperateMySQL()
    conn, cur = operatMySQl.get_operater()

    sql = "SELECT * FROM  stock_deal where " \
    "((stock_index > '300000' and stock_index < '700000') or " \
    "(stock_index > '150000' and stock_index < '200000') or " \
    "(stock_index > '000000' and stock_index < '100000')) group by stock_index"

    sql_read_row = "SELECT * FROM stock_deal where stock_index = {0};"
    sqli = "insert into stock_earnings values ({0},{1},'{2}','{3}');"
    df = pd.read_sql(sql, conn)
    print(len(df))
    df_result = pd.DataFrame(columns=['len','stock_index', 'stock_name', 'real_money' ])
    sum_r = 0.0
    for index,row in df.iterrows():
        sql_formated = sql_read_row.format(row['stock_index'])
        #print(sql_row)
        df_line = pd.read_sql(sql_formated, conn)
        #print(df_line)
        row_append = pd.DataFrame([dict(len=len(df_line),stock_index=row['stock_index'], stock_name =row['stock_name'], real_money=my_round(sum(df_line['real_money'])))])
        df_result = df_result.append(row_append, ignore_index=True)
        sum_r = sum_r + my_round(sum(df_line['real_money']))  #累计盈利

        sql_formated =sqli.format(len(df_line),my_round(sum(df_line['real_money'])),row['stock_index'],row['stock_name'])
        #print(row['stock_index'],row['stock_name'],my_round(sum(df_line['real_money'])), len(df_line))
        operatMySQl.execute(sql_formated)
    operatMySQl.commit()
    df_result=df_result.sort_values(by='real_money')
    #df_result=df_result.reset_index()

    #df_result.to_csv('d:\\result.csv')
    print(df_result)
    print(sum_r)


def query_earnings():
    operatMySQl = OperateMySQL()
    conn, cur = operatMySQl.get_operater()
    from_tabl = "SELECT stock_index,len,real_money,stock_name,name,industry,area,pe,outstanding,totals,reservedPerShare FROM  stock_earnings natural join stock_basic where "
    sh_stock = "(stock_index > '600000' and stock_index < '700000')"
    sz_stock = "(stock_index > '000000' and stock_index < '100000')"
    cy_stock = "(stock_index > '300000' and stock_index < '400000')"
    jj_stock = "(stock_index > '150000' and stock_index < '200000')"
    money_greater = "real_money>0"
    money_lower  =  "real_money<0"
    order_by = "order by real_money"
    sql_list = []
    sql_list.append(("沪市", "盈利", "{0} {1} and {2} {3} desc".format(from_tabl,sh_stock,money_greater,order_by)))
    sql_list.append(("深市", "盈利", "{0} {1} and {2} {3} desc".format(from_tabl,sz_stock,money_greater,order_by)))
    sql_list.append(("创业", "盈利", "{0} {1} and {2} {3} desc".format(from_tabl,cy_stock,money_greater,order_by)))
    sql_list.append(("基金", "盈利", "{0} {1} and {2} {3} desc".format(from_tabl,jj_stock,money_greater,order_by)))

    sql_list.append(("沪市", "亏损", "{0} {1} and {2} {3} asc".format(from_tabl,sh_stock,money_lower,order_by)))
    sql_list.append(("深市", "亏损", "{0} {1} and {2} {3} asc".format(from_tabl,sz_stock,money_lower,order_by)))
    sql_list.append(("创业", "亏损", "{0} {1} and {2} {3} asc".format(from_tabl,cy_stock,money_lower,order_by)))
    sql_list.append(("基金", "亏损", "{0} {1} and {2} {3} asc".format(from_tabl,jj_stock,money_lower,order_by)))

    sql_list.append(("沪市", "盈亏", "{0} {1} {2}".format(from_tabl,sh_stock,order_by)))
    sql_list.append(("深市", "盈亏", "{0} {1} {2}".format(from_tabl,sz_stock,order_by)))
    sql_list.append(("创业", "盈亏", "{0} {1} {2}".format(from_tabl,cy_stock,order_by)))
    sql_list.append(("基金", "盈亏", "{0} {1} {2}".format(from_tabl,jj_stock,order_by)))

    sql_list.append(("合计", "盈亏", "SELECT * FROM  stock_earnings "))
    #"((stock_index > '300000' and stock_index < '700000') or (stock_index > '150000' and stock_index < '200000') or (stock_index > '000000' and stock_index < '100000'))"))

    file_object = codecs.open('d:\\result.txt', 'w', "utf-8")
    for sql in sql_list:
        df = pd.read_sql(sql[2], conn)
        reslut_str = "{0},{1},{2}只, {3}笔, {4} \r\n".format(sql[0], sql[1], len(df), sum(df['len']), my_round(sum(df['real_money'])))
        file_object.write(reslut_str)
        #print(reslut_str)
        #print(df.head(10))
        #file_object.write(df.head(10).describe())
        df.head(10).to_csv('d:\\result.txt', index=False)
    file_object.close()

def query_total_deal_money():
    operatMySQl = OperateMySQL()
    conn, cur = operatMySQl.get_operater()

    sql = "SELECT * FROM  stock_deal where " \
    "((stock_index > '300000' and stock_index < '700000') or " \
    "(stock_index > '150000' and stock_index < '200000') or " \
    "(stock_index > '000000' and stock_index < '100000'))"

    df = pd.read_sql(sql, conn)
    #print(df['stock_index'],df['stock_name'])
    print(len(df))
if __name__ == '__main__':
    #init_sql_by_excel()
    #query_amount_transferred_into_account()
    #query_reverse_repo()
    #query_fees_stamp_duty()
    #query_total_deal_money()
    #query_stock()
    query_earnings()

