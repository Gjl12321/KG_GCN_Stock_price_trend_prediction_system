import os
import re
import math
import time
import json
import requests
import akshare as ak
import numpy as np
import pandas as pd
from requests.adapters import HTTPAdapter
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render

from py2neo import Graph, Node, Relationship, cypher


# 金十
def get_js_news(start_time, end_time):
    url = "https://flash-api.jin10.com/get_flash_list"
    header = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "handleerror": "true",
        "origin": "https://www.jin10.com",
        "pragma": "no-cache",
        "referer": "https://www.jin10.com/",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "x-app-id": "bVBF4FyRTn5NJF5n",
        "x-version": "1.0.0",
    }
    queryParam = {
        "vip": "1",
        "max_time": end_time,
        "channel": "-8200",
    }

    news_list = []

    Data = requests.get(url, queryParam, headers=header).json()['data']
    length = len(Data)

    while length > 0:
        for i in range(length):
            try:
                if Data[i]['type'] == 0 and ('pic' not in Data[i]['data'].keys() or not Data[i]['data']['pic']):
                    content = Data[i]['data']['content']
                    news_list.append([Data[i]['time'], content])
            except Exception as e:
                print(e)
                continue

        queryParam['max_time'] = Data[length - 1]['time']
        if queryParam['max_time'] <= start_time:
            break
        try:
            s = requests.Session()
            s.mount('http://', HTTPAdapter(max_retries=3))
            s.mount('https://', HTTPAdapter(max_retries=3))
            Data = requests.get(url, queryParam, timeout=5, headers=header).json()['data']
            length = len(Data)
        except Exception as e:
            print(e)
            break

    news_list = sorted(list(set([tuple(t) for t in list(filter(lambda x: x[0] >= start_time, news_list))])), key=lambda x: x[0], reverse=False)
    return news_list


def get_update_news():
    news_list_daily = []

    deadline = '2022-05-28 23:00:00'
    next_start_time = '2022-05-28 00:00:00'
    start = [-1, -1, -1, -1, -1]

    while True:
        now = time.localtime(time.time())
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        if now_time >= deadline:
            break

        if now[:5] != start:
            print(now_time, end='\t:\t')
            start = now[:5]
            temp = get_js_news(start_time=next_start_time, end_time=now_time)
            length = len(temp)
            next_start_time = temp[-1][0]

            for item in temp:
                if item not in news_list_daily:
                    news_list_daily.append(item)
                else:
                    length -= 1

            with open('F:/data/KG_GCN_Stock_price_trend_prediction_system/news/js_news.json', 'w') as sf:
                json.dump(news_list_daily, sf)

            print(length, len(news_list_daily))

            time.sleep(max(0, 50-now[5]))


# 财联社
def get_cls_news(news_len=10000, time_filter='none') -> pd.DataFrame:
    """
    财联社-今日快讯
    https://www.cls.cn/searchPage?keyword=%E5%BF%AB%E8%AE%AF&type=all
    :return: 财联社-今日快讯
    :rtype: pandas.DataFrame
    """
    url = "https://www.cls.cn/api/sw"
    params = {"app": "CailianpressWeb", "os": "web", "sv": "7.5.5"}
    headers = {
        "Host": "www.cls.cn",
        "Connection": "keep-alive",
        "Content-Length": "112",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://www.cls.cn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    payload = {
        "type": "telegram",
        "keyword": "快讯",
        "page": 0,
        "rn": news_len,
        "os": "web",
        "sv": "7.2.2",
        "app": "CailianpressWeb",
    }
    r = requests.post(url, headers=headers, params=params, json=payload)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"]["telegram"]["data"])
    temp_df = temp_df[["descr", "time"]]
    temp_df["descr"] = temp_df["descr"].astype(str).str.replace("</em>", "")
    temp_df["descr"] = temp_df["descr"].str.replace("<em>", "")
    temp_df["time"] = pd.to_datetime(temp_df["time"], unit="s").dt.date
    temp_df['time'] = [str(i) for i in temp_df['time']]
    if time_filter != 'none':
        temp_df = temp_df[temp_df['time'] == time_filter]
    return temp_df


def get_news():
    result = {}

    # 金十新闻
    if True:
        with open(settings.DATA_ROOT + '/news/js_news.json', 'r') as rf:
            temp = json.load(rf)
        result['js'] = [
            {
                'id': i,
                'date': temp[i][0][11:-3],
                'content': temp[i][1],
                'height': math.ceil(len(temp[i][1]) / 46) * 20 + 20,
                'line_height': math.ceil(len(temp[i][1]) / 46) * 20,
            } for i in range(len(temp))
        ]
        result['js'] = sorted(result['js'], key=lambda x: x['date'], reverse=True)

    # 财联社
    if True:
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        # df = get_cls_news(news_len=1000, time_filter=today)
        df = get_cls_news(news_len=1000)
        result['cls'] = [
            {
                'id': i,
                'date': df['time'][i],
                'content': df['descr'][i],
                'height': math.ceil(len(df['descr'][i]) / 46) * 20 + 20,
                'line_height': math.ceil(len(df['descr'][i]) / 46) * 20,
            } for i in range(df.shape[0])
        ]

    # Tushare
    if True:
        with open(settings.DATA_ROOT + '/news/20220528.json', 'r') as rf:
            temp = json.load(rf)

        result['tushare'] = {
            'news_1': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['公司']],
            'news_2': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['国际']],
            'news_3': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['疫情']],
            'news_4': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['焦点']],
            'news_5': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['市场']],
            'news_6': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['宏观']],
            'news_7': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['A股']],
            'news_8': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['行业']],
            'news_9': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['观点']],
            'news_10': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['新浪财经']['其他']],
            'news_11': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['东方财富']['全球股市']],
            'news_12': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['东方财富']['上市公司']],
            'news_13': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['东方财富']['要闻']],
            'news_14': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['东方财富']['商品']],
            'news_15': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['同花顺']['7 × 24 小时全球财经资讯直播']],
            'news_16': [[i[0], math.ceil(len(i[2]) / 46) * 20 + 20, math.ceil(len(i[2]) / 46) * 20, i[2]] for i in temp['云财经']['全部']]
        }

    return result
# -------------------------------------------------------------------------------------------------


# 新闻列表
def news_list(request):
    news = get_news()
    res_dist = {
        'news_list': news['tushare']
    }
    return render(request, 'news/news_list.html', res_dist)


def news_daily(request, news_type):
    news = get_news()
    res_dist = {
        'type_name': news_type,
        'news_list': news['js'] if news_type == 'js' else news['cls']
    }
    return render(request, 'news/news_daily.html', res_dist)
# -------------------------------------------------------------------------------------------------


# 获取子图
def get_relations(data):
    graph = Graph("bolt://localhost:11003", auth=("neo4j", "gjl19971213"))
    nodes = []
    links = []

    if 'stock_1' in data.keys() and 'stock_2' not in data.keys():
        stock = data['stock_1']
        for i in graph.run('match (a:Stock {name: "' + stock + '"})-[r]->(b) return a,r,b').data():
            a = {'name': dict(i['a'])['name'], 'category': re.match(r'^\(.*?:(.*) \{', str(i['a'])).groups()[0]}
            b = {'name': dict(i['b'])['name'], 'category': re.match(r'^\(.*?:(.*) \{', str(i['b'])).groups()[0]}
            r_item = re.match(r'^\((.*?)\).*:(.*?) \{.*->\((.*?)\)', str(i['r'])).groups()
            links.append({'source': r_item[0], 'target': r_item[2], 'value': r_item[1]})
            if a not in nodes:
                nodes.append(a)
            if b not in nodes:
                nodes.append(b)
    else:
        stock_1 = data['stock_1']
        stock_2 = data['stock_2']
        for i in graph.run(
                'match (a:Stock {name: "' + stock_1 + '"})-[r1]-(b)-[r2]-(c:Stock {name: "' + stock_2 + '"}) return a,r1,b,r2,c').data():
            a = {'name': dict(i['a'])['name'], 'category': re.match(r'^\(.*?:(.*) \{', str(i['a'])).groups()[0]}
            b = {'name': dict(i['b'])['name'], 'category': re.match(r'^\(.*?:(.*) \{', str(i['b'])).groups()[0]}
            c = {'name': dict(i['c'])['name'], 'category': re.match(r'^\(.*?:(.*) \{', str(i['c'])).groups()[0]}
            r1_item = re.match(r'^\((.*?)\).*:(.*?) \{.*->\((.*?)\)', str(i['r1'])).groups()
            r2_item = re.match(r'^\((.*?)\).*:(.*?) \{.*->\((.*?)\)', str(i['r2'])).groups()
            links.append({'source': r1_item[0], 'target': r1_item[2], 'value': r1_item[1]})
            links.append({'source': r2_item[0], 'target': r2_item[2], 'value': r2_item[1]})
            if a not in nodes:
                nodes.append(a)
            if b not in nodes:
                nodes.append(b)
            if c not in nodes:
                nodes.append(c)
    return nodes, links


# 知识图谱
def knowledge_graph(request):
    stock_1 = str(request.GET.get('stock1', ''))
    stock_2 = str(request.GET.get('stock2', ''))
    stock = [stock_1, stock_2]

    if stock_1 != '' and stock_2 != '':
        nodes, links = get_relations({'stock_1': stock_1, 'stock_2': stock_2})
        for node in get_relations({'stock_1': stock_1})[0]:
            if node not in nodes:
                nodes.append(node)
        for link in get_relations({'stock_1': stock_1})[1]:
            if link not in links:
                links.append(link)
        for node in get_relations({'stock_1': stock_2})[0]:
            if node not in nodes:
                nodes.append(node)
        for link in get_relations({'stock_1': stock_2})[1]:
            if link not in links:
                links.append(link)

    elif stock_1 != '' or stock_2 != '':
        nodes, links = get_relations({'stock_1': stock_1 if stock_1 != '' else stock_2})
    else:
        nodes = []
        links = []

    categories = [
        {'name': 'Stock', 'color': '#3a6df0'},
        {'name': 'Concept', 'color': '#4cae4c'},
        {'name': 'Industry', 'color': '#d58512'},
        {'name': 'Shareholder', 'color': '#d6e9c6'},
        {'name': 'People', 'color': '#cf4af3'}
    ]

    history = [
        {
            'stock_1': '东贝集团',
            'stock_2': 'ST高升'
        }, {
            'stock_1': '盛天网络'
        }, {
            'stock_1': '盛天网络'
        }, {
            'stock_1': '盛天网络'
        }, {
            'stock_1': '盛天网络'
        }, {
            'stock_1': '盛天网络'
        }, {
            'stock_1': '盛天网络'
        }
    ]

    res_dist = {
        'stock_list': [stock_1, stock_2],
        'stock': stock,
        'nodes': nodes,
        'links': links,
        'categories': categories,
        'history': history
    }
    return render(request, 'kg/knowledge_graph.html', res_dist)
# -------------------------------------------------------------------------------------------------


# 股票预测
def predict(request):
    stock = ''
    result = 0.0

    res_dist = {
        'result': result
    }
    return render(request, 'predict/predict.html', res_dist)
# -------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    # get_update_news(deadline='2022-03-02 00:00:00', next_start_time='2022-03-01 00:00:00')
    # today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # df = get_cls_news(news_len=1000, time_filter=today)
    # print(df)

    print()










