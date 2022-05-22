import os
import re
import time
import json
import datetime
import requests
import akshare as ak
import numpy as np
import pandas as pd
from py2neo import Graph, Node, Relationship, cypher
from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from requests.adapters import HTTPAdapter


def get_company_info():
    with open('F:/python_project/gjl_stock_system/price/stock_dict.json', 'r') as rf:
        temp = json.load(rf)
    stocks = list(temp.keys())
    browser = webdriver.Chrome(executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')
    for stock_code in stocks:
        url = 'https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/'+stock_code[2:]+'.phtml'
        try:
            browser.get(url)
            time.sleep(3)
            table = browser.find_elements(by=By.XPATH, value='//*[@id="comInfo1"]/tbody/tr')
            time.sleep(1)
            info = {}

            for tr in table:
                if tr.text != '':
                    titles = []
                    contents = []
                    for i in tr.find_elements(by=By.CLASS_NAME, value='ct'):
                        titles.append(i.text)
                    for i in tr.find_elements(by=By.CLASS_NAME, value='cc')+tr.find_elements(by=By.CLASS_NAME, value='ccl'):
                        contents.append(i.text)
                    # print(titles, contents)
                    if len(titles) == len(contents):
                        for i in range(len(titles)):
                            info[titles[i]] = contents[i]
                    else:
                        info['other'] = [titles, contents]

            with open('F:/python_project/gjl_stock_system/price/data/company_info/'+stock_code+'.json', 'w') as sf:
                json.dump(info, sf)
        except Exception as e:
            print(stock_code, url, e)
        else:
            print(stock_code, 'finish')


def get_minute_price():
    with open('F:/python_project/gjl_stock_system/price/stock_dict.json', 'r') as rf:
        temp = json.load(rf)

    for stock_code in temp.keys():
        if os.path.exists('F:/python_project/gjl_stock_system/price/data/minute_price/' + stock_code + '.json'):
            with open('F:/python_project/gjl_stock_system/price/data/minute_price/' + stock_code + '.json', 'r') as rf:
                data = json.load(rf)
            last_day = data['days'][-1]
        else:
            data = {
                'len': 0,
                'days': [],
                'price': []
            }
            last_day = '2000-01-01'
        try:

            df = ak.stock_zh_a_minute(symbol=stock_code, period='1')

            for index in range(df.shape[0]):
                first_day = df['day'][index][:10]
                if first_day > last_day:
                    last_day = first_day
                    data['len'] += 1
                    data['days'].append(first_day)
                    data['price'].append([{
                        'time': df['day'][index],
                        'open': df['open'][index],
                        'high': df['high'][index],
                        'low': df['low'][index],
                        'close': df['close'][index],
                        'volume': df['volume'][index]
                    }])
                elif first_day == last_day:
                    data['price'][data['len'] - 1].append({
                        'time': df['day'][index],
                        'open': df['open'][index],
                        'high': df['high'][index],
                        'low': df['low'][index],
                        'close': df['close'][index],
                        'volume': df['volume'][index]
                    })
                else:
                    continue

            with open('F:/python_project/gjl_stock_system/price/data/minute_price/' + stock_code + '.json', 'w') as sf:
                json.dump(data, sf)
        except Exception as e:
            print(stock_code, 'error', e)
        else:
            print(stock_code, 'finish')


def get_history_price():
    with open('F:/python_project/gjl_stock_system/price/data/stock_code_list.json', 'r') as rf:
        stock_code_list = json.load(rf)
    # stock_code_list = ['bj430047']
    start_date = "19700101"
    today = time.strftime('%Y%m%d', time.localtime(time.time()))
    error_stock_code = []

    for stock_code in stock_code_list:
        try:
            df = ak.stock_zh_a_hist(symbol=stock_code[2:], period='daily', start_date=start_date, end_date=today)
            history_price = {
                'dates': list(df['日期']),
                'data': [[
                    float(df['开盘'][index]),
                    float(df['收盘'][index]),
                    float(df['最低'][index]),
                    float(df['最高'][index]),
                    int(df['成交量'][index])
                ] for index in range(df.shape[0])],
                'volumes': [str(df['成交量'][index]) for index in range(df.shape[0])],
                'other': {
                    'name': ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率'],
                    'value': {
                        'date': [str(df['日期'][index]) for index in range(df.shape[0])],
                        'open': [str(df['开盘'][index]) for index in range(df.shape[0])],
                        'close': [str(df['收盘'][index]) for index in range(df.shape[0])],
                        'high': [str(df['最高'][index]) for index in range(df.shape[0])],
                        'low': [str(df['最低'][index]) for index in range(df.shape[0])],
                        'volumes': [str(df['成交量'][index]) for index in range(df.shape[0])],
                        'turnover': [str(df['成交额'][index]) for index in range(df.shape[0])],
                        'amplitude': [str(df['振幅'][index]) + '%' for index in range(df.shape[0])],
                        'Chg': [str(df['涨跌幅'][index]) + '%' for index in range(df.shape[0])],
                        'change': [str(df['涨跌额'][index]) for index in range(df.shape[0])],
                        'turnover_rate': [str(df['换手率'][index]) + '%' for index in range(df.shape[0])]
                    }
                }
            }
            with open('F:/python_project/gjl_stock_system/price/data/history_price/'+stock_code+'.json', 'w') as sf:
                json.dump(history_price, sf)
        except Exception as e:
            print(stock_code, 'error', e)
            error_stock_code.append(stock_code)
        else:
            print(stock_code, 'finish')
        time.sleep(2)

    print(error_stock_code)


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


def get_fast_news(timestamp: str = "2021-06-05 20:50:18") -> pd.DataFrame:
    """
    金十数据-市场快讯
    https://www.jin10.com/
    :param timestamp: choice of {'最新资讯', '最新数据'}
    :type timestamp: str
    :return: 市场快讯
    :rtype: pandas.DataFrame
    """
    url = "https://flash-api.jin10.com/get_flash_list"
    params = {
        "channel": "-8200",
        "vip": "1",
        "t": "1625623640730",
        "max_time": timestamp,
    }
    headers = {
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
    r = requests.get(url, params=params, headers=headers)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"])
    temp_list = []
    for item in temp_df["data"]:
        if "content" in item.keys():
            temp_list.append(item["content"])
        elif "pic" in item.keys():
            temp_list.append(item["pic"])
        else:
            temp_list.append("-")
    temp_df = pd.DataFrame([temp_df["time"].to_list(), temp_list]).T
    temp_df.columns = ["datetime", "content"]
    return temp_df


def get_news():
    # df = get_stock_news(stock="601628")
    # for i in range(df.shape[0]):
    #     print(df['code'][i], df['title'][i], df['content'][i], df['public_time'][i], df['url'][i])

    # today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # df = get_daily_news(news_len=100, time_filter=today)
    # print(df)

    today = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    df = get_fast_news(timestamp=today)
    df = df.query('content != "-"')
    df.reset_index(inplace=True, drop=True)

    for i in range(df.shape[0]):
        df['content'][i] = re.sub(r'<.*>', '', df['content'][i]).replace(' ', '')
        if df['content'][i]:
            print(df['datetime'][i], df['content'][i])


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

    deadline = '2022-03-15 23:00:00'
    next_start_time = '2022-03-15 00:00:00'
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

            with open('data/js_news.json', 'w') as sf:
                json.dump(news_list_daily, sf)

            print(length, len(news_list_daily))

            time.sleep(max(0, 50-now[5]))


def get_news_info():
    option = webdriver.ChromeOptions()
    option.add_argument('--user-data-dir=C:/Users/admin/AppData/Local/Google/Chrome/User Data')
    browser = webdriver.Chrome(options=option, executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')
    data = {}

    for url, title in zip([
                'https://tushare.pro/news/news_sina#102',
                'https://tushare.pro/news/news_eastmoney',
                'https://tushare.pro/news/news_10jqka',
                'https://tushare.pro/news/news_yuncaijing',
                'https://tushare.pro/news/news_wallstreetcn'
            ], [
                '新浪财经',
                '东方财富',
                '同花顺',
                '云财经',
                '华尔街见闻'
            ]):
        data[title] = {}
        browser.get(url)
        time.sleep(3)
        types = browser.find_elements(by=By.XPATH, value='//*[@id="channel_head"]/span')
        type_len = len(types)

        for i in range(type_len):
            browser.find_element(by=By.XPATH, value='//*[@id="channel_head"]/span['+str(i+1)+']').click()
            time.sleep(2)
            type_name = browser.find_element(by=By.XPATH, value='//*[@id="channel_head"]/span['+str(i+1)+']').text
            divs = types[i].find_elements(by=By.XPATH, value='/html/body/div[1]/section/div/div[2]/div['+str(i+2)+']/div')
            data[title][type_name] = []

            for div in divs:
                class_name = div.get_attribute('class')
                if 'none_class' in class_name or 'key_news' in class_name:
                    date = div.find_element(by=By.CLASS_NAME, value='news_datetime').text
                    text = div.find_element(by=By.CLASS_NAME, value='news_content').text
                    data[title][type_name].append([date, class_name, text])

            print(title, type_name, len(data[title][type_name]))

    with open('F:/python_project/gjl_stock_system/price/data/news/20220315.json', 'w') as sf:
        json.dump(data, sf)


if __name__ == '__main__':
    # get_news()

    # get_js_news()

    # get_update_news()

    get_news_info()

    # get_company_info()

    # with open('F:/python_project/gjl_stock_system/price/data/company_info/sz300435.json', 'r') as rf:
    #     temp = json.load(rf)
    #
    # for key in temp.keys():
    #     print(key, temp[key])

    # print(get_daily_news())

    print()
