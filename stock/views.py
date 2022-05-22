import os
import time
import json
import requests
import akshare as ak
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from .models import Stock, Industry, Concept, HotConcept
from select_stock.models import SelectStock


def get_stock_news(stock: str = "601628") -> pd.DataFrame:
    """
    东方财富-个股新闻-最近 20 条新闻
    http://so.eastmoney.com/news/s?keyword=%E4%B8%AD%E5%9B%BD%E4%BA%BA%E5%AF%BF&pageindex=1&searchrange=8192&sortfiled=4
    :param stock: 股票代码
    :type stock: str
    :return: 个股新闻
    :rtype: pandas.DataFrame
    """
    url = "http://searchapi.eastmoney.com//bussiness/Web/GetCMSSearchList"
    params = {
        "type": "8196",
        "pageindex": "1",
        "pagesize": "20",
        "keyword": f"({stock})()",
        "name": "zixun",
        # "_": "1608800267874",
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "searchapi.eastmoney.com",
        "Pragma": "no-cache",
        "Referer": "http://so.eastmoney.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    r = requests.get(url, params=params, headers=headers)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["Data"])
    temp_df.columns = [
        "url",
        "title",
        "_",
        "public_time",
        "content",
    ]
    temp_df['code'] = stock
    temp_df = temp_df[
        [
            "code",
            "title",
            "content",
            "public_time",
            "url",
        ]
    ]
    temp_df["title"] = (
        temp_df["title"].str.replace(r"\(<em>", "", regex=True).str.replace(r"</em>\)", "", regex=True)
    )
    temp_df["content"] = (
        temp_df["content"].str.replace(r"\(<em>", "", regex=True).str.replace(r"</em>\)", "", regex=True)
    )
    temp_df["content"] = (
        temp_df["content"].str.replace(r"<em>", "", regex=True).str.replace(r"</em>", "", regex=True)
    )
    temp_df["content"] = temp_df["content"].str.replace(r"\u3000", "", regex=True)
    temp_df["content"] = temp_df["content"].str.replace(r"\r\n", " ", regex=True)
    return temp_df


def get_daily_news(news_len=10000, time_filter='none') -> pd.DataFrame:
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


def get_page_num(page_num, stocks_all_list):
    paginator = Paginator(stocks_all_list, 10)
    page_of_stocks = paginator.get_page(page_num)
    current_page_num = page_of_stocks.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    return page_of_stocks, page_range


def get_stocks_price(stocks):
    with open(settings.PRICE_ROOT + '/stock_dict.json', 'r', encoding='utf-8') as rf:
        stock_dict = json.load(rf)
    stock_price = []
    for stock in stocks.object_list:
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


def get_stock_class():
    res = {
        'shenwan_1': [],
        'shenwan_2': [],
        'shenwan_3': []
    }
    with open(settings.PRICE_ROOT + '/data/申万一级类别.json', 'r') as rf:
        temp = json.load(rf)
    for k in temp.keys():
        res['shenwan_1'].append(k)

    with open(settings.PRICE_ROOT + '/data/申万二级类别.json', 'r') as rf:
        temp = json.load(rf)
    for k in temp.keys():
        res['shenwan_2'].append(k)

    with open(settings.PRICE_ROOT + '/data/申万三级类别.json', 'r') as rf:
        temp = json.load(rf)
    for k in temp.keys():
        res['shenwan_3'].append(k)

    with open(settings.PRICE_ROOT + '/data/地域板块.json', 'r') as rf:
        temp = json.load(rf)
    res['place_of_stock'] = list(temp.keys())

    with open(settings.PRICE_ROOT + '/data/热门概念.json', 'r') as rf:
        temp = json.load(rf)
    res['hot_concept'] = list(temp.keys())

    temp = Concept.objects.all()
    res['concept'] = [i.name for i in temp]

    return res


def get_stock_list(show_list):
    if show_list in ['all', 'industry', 'hot_concept', 'concept', 'place']:
        stocks_list = Stock.objects.all()
        type_name = show_list
    elif '-' in show_list:
        stock_type_1 = show_list.split('-')[0]
        stock_type_2 = show_list.split('-')[1]
        type_name = stock_type_2
        if stock_type_1 == 'shenwan_1':
            stocks_list = Stock.objects.filter(shenwan_1=stock_type_2)
        elif stock_type_1 == 'shenwan_2':
            stocks_list = Stock.objects.filter(shenwan_2=stock_type_2)
        elif stock_type_1 == 'shenwan_3':
            stocks_list = Stock.objects.filter(shenwan_3=stock_type_2)
        elif stock_type_1 == 'hot_concept':
            try:
                hot_concept = HotConcept.objects.get(name=stock_type_2)
                stocks_list = Stock.objects.filter(stock_hot_concept=hot_concept)
            except:
                stocks_list = Stock.objects.all()
        elif stock_type_1 == 'concept':
            try:
                concept = Concept.objects.get(name=stock_type_2)
                stocks_list = Stock.objects.filter(stock_concept=concept)
            except:
                stocks_list = Stock.objects.all()
        elif stock_type_1 == 'place':
            stocks_list = Stock.objects.filter(stock_place=stock_type_2)
            type_name = stock_type_2
        else:
            stocks_list = Stock.objects.all()
    else:
        stocks_list = Stock.objects.all()
        type_name = show_list
    return type_name, stocks_list


def number_abbreviation(num):
    res = str(int(num))
    if len(res) > 12:
        res = str(round(float(res[:-9]) / 1000, 2)) + '万亿'
    elif len(res) > 8:
        res = str(round(float(res[:-5]) / 1000, 2)) + '亿'
    elif len(res) > 4:
        res = str(round(float(res[:-1]) / 1000, 2)) + '万'
    else:
        res = str(round(num, 2))
    return res


# 公司
def get_company_info(stock_code, root_path=settings.PRICE_ROOT):
    with open(root_path + '/data/company_info/'+stock_code+'.json', 'r') as rf:
        temp = json.load(rf)

    res = []
    for key in temp.keys():
        res.append({
            'key': key,
            'value': temp[key]
        })

    return res


def stock_list(request, show_list):
    type_name, stocks_list = get_stock_list(show_list)

    # 股票类别
    class_of_stock = get_stock_class()

    # 自选股票
    user = request.user
    if not user.is_authenticated:
        select_stocks = []
    else:
        select_stocks = [i.stock for i in SelectStock.objects.filter(user=user)]

    # 页码
    page_num = request.GET.get('page', 1)
    page_of_stocks, page_range = get_page_num(page_num, stocks_list)

    # 价格
    stock_price = get_stocks_price(page_of_stocks)

    res_dist = {
        'stocks': stock_price,
        'page_of_stocks': page_of_stocks,
        'page_range': page_range,
        'class_of_stock': class_of_stock,
        'type_name': type_name,
        'select_stocks': select_stocks
    }
    return render(request, 'stock/stock_list.html', res_dist)


def stock_detail(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)

    # 价格信息
    with open(settings.PRICE_ROOT + '/stock_dict.json', 'r', encoding='utf-8') as rf:
        stock_dict = json.load(rf)
    stock_price = stock_dict[stock.stock_code]

    # 历史价格信息
    with open(settings.PRICE_ROOT + '/data/history_price/' + stock.stock_code + '.json', 'r') as rf:
        history_price = json.load(rf)

    # 当前价格信息
    try:
        df = ak.stock_zh_a_spot_em()
        temp = df[df['代码'] == stock.stock_code[2:]]
        temp.reset_index(inplace=True, drop=True)
        df = ak.stock_individual_info_em(symbol=stock.stock_code[2:])

        data = {
            'new_price': round(temp['最新价'][0], 2),
            'Chg': str(round(temp['涨跌幅'][0], 2)) + '%',
            'change': str(round(temp['涨跌额'][0], 2)),
            'volumes': number_abbreviation(temp['成交量'][0]) + '手',
            'turnover': number_abbreviation(temp['成交额'][0]) + '元',
            'amplitude': temp['振幅'][0],
            'high': temp['最高'][0],
            'low': temp['最低'][0],
            'open': temp['今开'][0],
            'close': temp['昨收'][0],
            'value_ratio': temp['量比'][0],
            'turnover_ratio': temp['换手率'][0],
            'pe_ratio': temp['市盈率-动态'][0],
            'ptb_ratio': temp['市净率'][0],
            'total_value': number_abbreviation(df['value'][0]),  # 总市值
            'circulation_value': number_abbreviation(df['value'][1]),  # 流通市值
            'total_share_capital': df['value'][6],  # 总股本
            'tradable_shares': df['value'][7],  # 流通股
            'diff_price': temp['最新价'][0]-temp['昨收'][0],
            'diff_ratio': (temp['最新价'][0]-temp['昨收'][0]) / temp['昨收'][0] * 100,
        }
    except:
        data = {
            'new_price': '-',
            'Chg': '-',
            'change': '-',
            'volumes': '-',
            'turnover': '-',
            'amplitude': '-',
            'high': '-',
            'low': '-',
            'open': '-',
            'close': '-',
            'value_ratio': '-',
            'turnover_ratio': '-',
            'pe_ratio': '-',
            'ptb_ratio': '-',
            'total_value': '-',
            'circulation_value': '-',
            'total_share_capital': '-',
            'tradable_shares': '-'
        }

    # 个股新闻
    try:
        df = get_stock_news(stock=stock.stock_code[2:])
        stock_news = [
            {
                'code': df['code'][i],
                'title': df['title'][i].replace('\n', ''),
                'content': df['content'][i].replace('\n', ''),
                'public_time': df['public_time'][i],
                'url': df['url'][i]
            } for i in range(df.shape[0])
        ]
    except:
        stock_news = []

    # 公司信息
    try:
        company = get_company_info(stock.stock_code)
    except:
        company = []

    res_dist = {
        'stock_obj': stock,
        # 'industry': industry,
        # 'concepts': concepts,
        'stock_price': stock_price,
        # 'minute_price': minute_price,
        'history_price': history_price,
        'stock_news': stock_news,
        'summary_data': data,
        'company': company,
    }
    return render(request, 'stock/stock_detail.html', res_dist)


