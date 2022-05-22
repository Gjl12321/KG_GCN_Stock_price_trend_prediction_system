import json
import time
import requests
import MySQLdb
from tqdm import tqdm
import numpy as np
import pandas as pd
import akshare as ak
from akshare.utils import demjson
from akshare.stock.stock_zh_a_sina import _get_zh_a_page_count
from py2neo import Graph, Node, Relationship, cypher
from pyquery import PyQuery as pq
from akshare.stock.cons import (
    zh_sina_a_stock_payload,
    zh_sina_a_stock_url,
    zh_sina_a_stock_count_url,
    zh_sina_a_stock_hist_url,
    hk_js_decode,
    zh_sina_a_stock_hfq_url,
    zh_sina_a_stock_qfq_url,
    zh_sina_a_stock_amount_url,
)


def insert_mysql():
    df = pd.read_csv('../data/stock_info.csv', index_col=0)
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock', charset='utf8')
    cur = conn.cursor()

    sql = "insert into stock_stock (stock_code, stock_name, stock_exchange, stock_company, stock_start_date) values(%s, %s, %s, %s, %s)"
    cur.executemany(sql, [(df['代码'][i], df['名称'][i], '-', '-', df['上市时间'][i]) for i in range(df.shape[0])])

    # text = cur.execute("select * from stock_stock")
    # info = cur.fetchmany(text)
    # print(info)

    # cur.execute("delete from stock_stock where stock_code = 'sz000969'")

    cur.close()
    conn.commit()
    conn.close()


def insert_industry():
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock', charset='utf8')
    cur = conn.cursor()
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))

    for i in graph.run('match (n:Industry) return n').data():
        print(i['n']['指数代码'], i['n']['指数名称'])
        cur.execute("insert into stock_industry (code, name) values('"+i['n']['指数代码']+"', '"+i['n']['指数名称']+"')")

    cur.close()
    conn.commit()
    conn.close()


def insert_concept():
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock', charset='utf8')
    cur = conn.cursor()
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))

    for i in graph.run('match (n:Concept) return n').data():
        print(i['n']['概念名称'])
        cur.execute("insert into stock_concept (name) values('"+i['n']['概念名称']+"')")

    cur.close()
    conn.commit()
    conn.close()


def get_industry_of_stock():
    df = pd.read_csv('../data/stock_info.csv', index_col=0)
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))
    code_list = list(df['代码'])
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock', charset='utf8')
    cur = conn.cursor()

    # cur.execute('update stock_stock set stock_industry_id=null')

    for code in code_list:
        industry = graph.run('match (a:Stock{代码: "'+code+'"})-[r:industry_of]->(b:Industry) return b').data()
        if industry:
            industry_name = industry[0]['b']['name']
            industry_code = industry[0]['b']['指数代码']
            tmp = cur.execute('select * from stock_industry where code="'+industry_code+'"')
            industry_id = cur.fetchmany(tmp)[0][0]
            print(code, industry_code, industry_name, industry_id)
            cur.execute('update stock_stock set stock_industry_id=%d where stock_code="%s"' % (industry_id, code))
        else:
            print(code)
            continue
    cur.close()
    conn.commit()
    conn.close()


def get_concept_of_stock():
    df = pd.read_csv('../data/stock_info.csv', index_col=0)
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))
    code_list = list(df['代码'])
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock', charset='utf8')
    cur = conn.cursor()

    # cur.execute('update stock_stock set stock_industry_id=null')

    for code in code_list:
        print(code, end=': ')
        tmp = cur.execute('select * from stock_stock where stock_code="'+code+'"')
        stock_id = cur.fetchmany(tmp)[0][0]

        concept_list = graph.run('match (a:Stock{代码: "' + code + '"})-[r:concept_of]->(b:Concept) return b').data()
        if concept_list:
            for concept in concept_list:
                concept_name = concept['b']['name']
                tmp = cur.execute('select * from stock_concept where name="' + concept_name + '"')
                concept_id = cur.fetchmany(tmp)[0][0]
                print(concept_id, end='\t')
                cur.execute('insert into stock_stock_stock_concept (stock_id, concept_id) values(%d, %d)' % (stock_id, concept_id))
        else:
            print(code)
            continue
        print()
    cur.close()
    conn.commit()
    conn.close()


def get_shenwan_of_stock():
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock', charset='utf8')
    cur = conn.cursor()
    data_dict = {}
    with open('申万一级类别.json', 'r') as rf:
        data_dict['shenwan_1'] = json.load(rf)
    with open('申万二级类别.json', 'r') as rf:
        data_dict['shenwan_2'] = json.load(rf)
    with open('申万三级类别.json', 'r') as rf:
        data_dict['shenwan_3'] = json.load(rf)
    for class_name in data_dict['shenwan_1'].keys():
        for stock_item in data_dict['shenwan_1'][class_name]:
            print('shenwan_1', class_name, stock_item[0], stock_item[1])
            cur.execute('update stock_stock set shenwan_1="'+class_name+'" where stock_code="'+stock_item[0]+'";')
    for class_name in data_dict['shenwan_2'].keys():
        for stock_item in data_dict['shenwan_2'][class_name]:
            print('shenwan_2', class_name, stock_item[0], stock_item[1])
            cur.execute('update stock_stock set shenwan_2="'+class_name+'" where stock_code="'+stock_item[0]+'";')
    for class_name in data_dict['shenwan_3'].keys():
        for stock_item in data_dict['shenwan_3'][class_name]:
            print('shenwan_3', class_name, stock_item[0], stock_item[1])
            cur.execute('update stock_stock set shenwan_3="'+class_name+'" where stock_code="'+stock_item[0]+'";')

    cur.close()
    conn.commit()
    conn.close()


def insert_hot_concept():
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock', charset='utf8')
    cur = conn.cursor()
    with open('热门概念.json', 'r') as rf:
        temp = json.load(rf)

    for concept_name in temp.keys():
        cur.execute("insert into stock_hotconcept (name) values('"+concept_name+"')")

    cur.close()
    conn.commit()
    conn.close()


def get_hot_concept_of_stock():
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock', charset='utf8')
    cur = conn.cursor()
    with open('热门概念.json', 'r') as rf:
        temp = json.load(rf)

    for concept_name, stock_list in temp.items():
        hot_concept_id = cur.fetchmany(cur.execute('select * from stock_hotconcept where name="'+concept_name+'"'))[0][0]
        print(concept_name, hot_concept_id)

        if stock_list:
            for stock in stock_list:
                try:
                    stock_id = cur.fetchmany(cur.execute('select * from stock_stock where stock_code="'+stock[0]+'"'))[0][0]
                except:
                    pass
                else:
                    cur.execute('insert into stock_stock_stock_hot_concept (stock_id, hotconcept_id) values(%d, %d)' % (stock_id, hot_concept_id))
        else:
            continue

    cur.close()
    conn.commit()
    conn.close()


def insert_place():
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='gjl19971213', db='gjl_stock',
                           charset='utf8')
    cur = conn.cursor()
    with open('地域板块.json', 'r') as rf:
        temp = json.load(rf)
    cnt = 0
    for place in temp.keys():
        for stock in temp[place]:
            cur.execute('update stock_stock set stock_place="'+place+'" where stock_code="'+stock[0]+'"')
    cur.close()
    conn.commit()
    conn.close()


def test_db():
    conn = MySQLdb.connect(host='120.46.158.255', port=3306, user='root', passwd='GJLgjl_19971213', db='mysql', charset='utf8')
    cur = conn.cursor()

    text = cur.execute("select user,host from user")
    info = cur.fetchmany(text)
    print(info)

    # cur.execute("delete from stock_stock where stock_code = 'sz000969'")

    cur.close()
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # insert_mysql()

    # insert_industry()

    # insert_concept()

    # get_industry_of_stock()

    # get_concept_of_stock()

    # get_shenwan_of_stock()

    # insert_hot_concept()

    # get_hot_concept_of_stock()

    # insert_place()
    print()


