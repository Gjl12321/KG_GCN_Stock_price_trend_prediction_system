import math
import os
import time
import json
import requests
import akshare as ak
import pandas as pd
from django.shortcuts import render, get_object_or_404
from requests.adapters import HTTPAdapter
from django.conf import settings
from stock.models import Stock


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


def get_stocks_price(stocks):
    with open(settings.DATA_ROOT + '/stock_dict.json', 'r', encoding='utf-8') as rf:
        stock_dict = json.load(rf)
    stock_price = []
    for stock in stocks:
        if stock.stock_code in stock_dict:
            stock_data = stock_dict[stock.stock_code]
            stock_price.append({
                'stock': stock,
                'last_price': str(round(stock_data['last_price'], 2)) + (
                    '0' if str(round(stock_data['last_price'], 2))[-2] == '.' else ''),  # 最新价格
                'diff_price': str(round(stock_data['diff_price'], 2)) + (
                    '0' if str(round(stock_data['diff_price'], 2))[-2] == '.' else ''),  # 涨跌额
                'diff_ratio': str(round(stock_data['diff_ratio'], 2)) + (
                    '0' if str(round(stock_data['diff_ratio'], 2))[-2] == '.' else '') + '%',  # 涨跌幅
                'max_price': str(round(stock_data['max_price'], 2)) + (
                    '0' if str(round(stock_data['max_price'], 2))[-2] == '.' else ''),  # 最高
                'min_price': str(round(stock_data['min_price'], 2)) + (
                    '0' if str(round(stock_data['min_price'], 2))[-2] == '.' else ''),  # 最低
                'sign': 'red' if stock_data['diff_price'] > 0 else 'green' if stock_data['diff_price'] < 0 else 'grey',
            })
    return stock_price


def home(request):
    stocks = [
        Stock.objects.get(stock_code='bj830946'),
        Stock.objects.get(stock_code='bj430198'),
        Stock.objects.get(stock_code='sh601169')
    ]
    stock_price = get_stocks_price(stocks)
    df = get_cls_news(news_len=1000)
    data = {
        'news': [
            {
                'id': i,
                'date': df['time'][i],
                'content': df['descr'][i],
                'height': math.ceil(len(df['descr'][i]) / 46) * 20 + 20,
                'line_height': math.ceil(len(df['descr'][i]) / 46) * 20,
            } for i in range(3)
        ],
        'stocks': stock_price
    }
    return render(request, 'home.html', data)

