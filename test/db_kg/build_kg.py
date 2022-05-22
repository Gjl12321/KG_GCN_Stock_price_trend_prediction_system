import time
import numpy as np
import pandas as pd
import akshare as ak
from py2neo import Graph, Node, Relationship, cypher
from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def get_stock_info():
    temp = []
    data = ak.stock_zh_a_spot()
    # data = pd.read_csv('F:/python_project/stock/data/stock.csv', index_col=0)
    for i in range(data.shape[0]):
        try:
            info = ak.stock_individual_info_em(symbol=data['代码'][i][2:])
        except:
            print(data['代码'][i])
        else:
            temp.append(
                [
                    data['代码'][i],
                    data['名称'][i],
                    info['value'][2],
                    info['value'][0],
                    info['value'][1],
                    info['value'][6],
                    info['value'][7],
                    info['value'][3]
                ]
            )
        if i % 10 == 0:
            print(i)

    df = pd.DataFrame({
        '代码': [i[0] for i in temp],
        '名称': [i[1] for i in temp],
        '行业': [i[2] for i in temp],
        '总市值': [i[3] for i in temp],
        '流通市值': [i[4] for i in temp],
        '总股本': [i[5] for i in temp],
        '流通股': [i[6] for i in temp],
        '上市时间': [i[7] for i in temp]
    })
    print(df)

    df.to_csv('stock_info.csv')


def stock_info_create_node():
    df = pd.read_csv('/data/stock_info.csv', index_col=0)
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))
    graph.run("MATCH (a:Stock) DELETE a")
    for i in range(df.shape[0]):
        graph.run("""create (a:Stock {
            name: "%s",
            代码: "%s",
            名称: "%s",
            行业: "%s",
            总市值: "%s",
            流通市值: "%s",
            总股本: "%s",
            流通股: "%s",
            上市时间: "%s"
        })""" % (
            df['名称'][i],
            df['代码'][i],
            df['名称'][i],
            df['行业'][i],
            df['总市值'][i],
            df['流通市值'][i],
            df['总股本'][i],
            df['流通股'][i],
            df['上市时间'][i]
        ))

        # print(graph.run("MATCH (a:A)-[r]->(b:B) RETURN a,r,b LIMIT 25").to_data_frame())


def industry_link_to_stock():
    temp = []
    df = ak.sw_index_spot()
    for i in range(df.shape[0]):
        industry_stock = ak.sw_index_cons(index_code=df['指数代码'][i])

        temp.append({
            '指数代码': df['指数代码'][i],
            '指数名称': df['指数名称'][i],
            '股票': [{
                'stock_code': industry_stock['stock_code'][i],
                'stock_name': industry_stock['stock_name'][i],
                'start_date': str(industry_stock['start_date'][i]),
                'weight': str(industry_stock['weight'][i])
            } for i in range(industry_stock.shape[0])]
        })

    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))
    for i in temp:
        if len(graph.run('match (a:Industry) where a.name="' + i['指数名称'] + '" return a').data()) == 0:
            graph.run(
                'create (a:Industry {name: "' + i['指数名称'] + '", 指数代码: "' + i['指数代码'] + '", 指数名称: "' + i['指数名称'] + '"})')
        else:
            pass
            # print(str(i['指数名称']) + ' has existed')

        for stock in i['股票']:
            if len(graph.run('match (a:Stock) where a.name = "' + stock['stock_name'] + '" return a').data()) == 0:
                print(str(stock['stock_name']) + ' not found')
            else:
                if len(graph.run(
                        'match (a:Stock)-[r:industry_of]->(b:Industry) where a.name = "%s" and b.name = "%s" return a,r,b' % (
                        stock['stock_name'], i['指数名称'])).data()) > 0:
                    graph.run(
                        'match (a:Stock)-[r:industry_of]->(b:Industry) where a.name = "%s" and b.name = "%s" delete r' % (
                        stock['stock_name'], i['指数名称']))

                graph.run("""
                    match (a:Stock), (b:Industry)
                    where a.name = "%s" and b.name = "%s"
                    create (a)-[r:industry_of {start_date: "%s", weight: "%s"}]->(b)
                """ % (stock['stock_name'], i['指数名称'], stock['start_date'], stock['weight']))


def people_link_to_stock():
    browser = webdriver.Chrome()
    df = pd.read_csv('/data/stock_info.csv', index_col=0)
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))

    for i in range(df.shape[0]):
        code = df['代码'][i]
        name = df['名称'][i]
        try:
            url = 'https://emweb.eastmoney.com/PC_SanBanF10/CompanyInfo/index?color=web&code=' + code[2:] + (
                '.SH' if code[:2] == 'sh' else '.BJ' if code[:2] == 'bj' else '.SZ')
            print(url)
            browser.get(url)
            time.sleep(1)
            text = browser.find_element(By.ID, 'div_ggjj').text.split('\n')
            while len(text) == 0:
                time.sleep(1)
                text = browser.find_element(By.ID, 'div_ggjj').text.split('\n')
            for j in text[1:]:
                tmp = j.split(' ')
                print(' '.join(tmp[:-5]), tmp[-5], tmp[-4], tmp[-3], tmp[-2], tmp[-1])
                graph.run("""
                    create (a:People {name: "%s", 姓名: "%s", 职务: "%s", 任职时间: "%s", 学历: "%s", 年龄: "%s", 性别: "%s"}) with a match (b:Stock) where b.代码="%s" with a,b create (a)-[r:employ_of]->(b)
                """ % (' '.join(tmp[:-5]), ' '.join(tmp[:-5]), tmp[-5], tmp[-4], tmp[-3], tmp[-2], tmp[-1], code))
        except:
            print('-------------------- ' + code, name + ' --------------------')


def holder_link_to_stock():
    browser = webdriver.Chrome()
    df = pd.read_csv('/data/stock_info.csv', index_col=0)
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))

    for i in range(df.shape[0]):
        code = df['代码'][i]
        name = df['名称'][i]
        sign = True
        cnt = 1

        while sign:
            try:
                url = 'https://emweb.eastmoney.com/PC_SanBanF10/Shareholders/index?color=web&code=' + code[2:] + (
                    '.SH' if code[:2] == 'sh' else '.BJ' if code[:2] == 'bj' else '.SZ') + '#sdgd-0'
                print(url)
                browser.get(url)
                time.sleep(cnt)
                text = browser.find_element(By.ID, 'div_sdgd').text.split('名次 股东名称')[1].replace('\'', '').replace('"',
                                                                                                                  '').split(
                    '\n')[1:]

                for j in text:
                    tmp = j.split(' ')
                    print(' '.join(tmp[1:-4]), tmp[-4], tmp[-3], tmp[-2], tmp[-1])
                    if len(graph.run(
                            'match (a:Shareholder) where a.name="' + ' '.join(tmp[1:-4]) + '" return a').data()) == 0:
                        graph.run('create (a:Shareholder {name: "' + ' '.join(tmp[1:-4]) + '", 股东名称: "' + ' '.join(tmp[
                                                                                                                   1:-4]) + '"}) with a match (b:Stock) where b.代码="' + code + '" with a,b create (b)-[r:hold_of {持股比例: "' +
                                  tmp[-3] + '"}]->(a)')
                    else:
                        graph.run('match (a:Shareholder),(b:Stock) where a.name="' + ' '.join(
                            tmp[1:-4]) + '" and b.代码="' + code + '" with a,b create (b)-[r:hold_of {持股比例: "' + tmp[
                                      -3] + '"}]->(a)')
                sign = False
            except:
                cnt += 1
                print('-------------------- ' + code, name + ' --------------------', cnt)
        print(i, df.shape[0])


def concept_link_to_stock():
    browser = webdriver.Chrome()
    df = pd.read_csv('/data/stock_info.csv', index_col=0)
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))

    for i in range(df.shape[0]):
        code = df['代码'][i]
        name = df['名称'][i]
        sign = True
        cnt = 1

        while sign:
            try:
                url = 'https://emweb.securities.eastmoney.com/PC_HSF10/CoreConception/Index?type=web&code=' + code
                print(url)
                browser.get(url)
                time.sleep(cnt)
                text = browser.find_element(By.ID, 'templateDiv').text.split('所属板块 ')[1].split('\n')[0].split(' ')

                for j in text:
                    if len(graph.run('match (a:Concept) where a.name="' + j + '" return a').data()) == 0:
                        graph.run(
                            'create (a:Concept {name: "' + j + '", 概念名称: "' + j + '"}) with a match (b:Stock) where b.代码="' + code + '" with a,b create (b)-[r:concept_of]->(a)')
                    else:
                        graph.run(
                            'match (a:Concept),(b:Stock) where a.name="' + j + '" and b.代码="' + code + '" with a,b create (b)-[r:concept_of]->(a)')
                sign = False
            except:
                if code[:2] == 'bj':
                    sign = False
                cnt += 1
                print('-------------------- ' + code, name + ' --------------------', cnt)
        print(i, df.shape[0])


def gjl_test():

    # df = pd.read_csv('../data/stock_info.csv', index_col=0)
    # print(df.shape[0])

    graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))
    data = graph.run('match (a:Stock)-[r]-(b:People) return a,b').data()
    print(len(data))


if __name__ == '__main__':
    # get_stock_info()
    # print('get_stock_info')
    gjl_test()

