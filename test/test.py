import json
import os
import nni
import time
import random
import numpy as np
import pandas as pd
import akshare as ak
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, precision_score, recall_score, precision_recall_curve, auc, roc_auc_score, accuracy_score
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.data.dataset import Dataset


def get_history_price():
    with open('F:/data/KG_GCN_Stock_price_trend_prediction_system/stock_code_list.json', 'r') as rf:
        stock_code_list = json.load(rf)
    # stock_code_list = ['bj430047']
    start_date = "20220101"
    today = time.strftime('%Y%m%d', time.localtime(time.time()))
    error_stock_code = []

    for stock_code in stock_code_list:
        start = time.time()

        if os.path.exists('F:/data/KG_GCN_Stock_price_trend_prediction_system/history_price/' + stock_code + '.json'):
            with open('F:/data/KG_GCN_Stock_price_trend_prediction_system/history_price/' + stock_code + '.json', 'r') as rf:
                temp = json.load(rf)
            start_date = temp['dates'][-1]
        else:
            temp = {
                'dates': [],
                'data': [],
                'volumes': [],
                'other': {
                    'value': {
                        'date': [],
                        'open': [],
                        'close': [],
                        'high': [],
                        'low': [],
                        'volumes': [],
                        'turnover': [],
                        'amplitude': [],
                        'Chg': [],
                        'change': [],
                        'turnover_rate': []
                    }
                }
            }

        print(stock_code[2:], '\t', end='\t')
        try:
            df = ak.stock_zh_a_hist(symbol=stock_code[2:], period='daily', start_date=start_date, end_date=today)
            history_price = {
                'dates': temp['dates'] + list(df['??????']),
                'data': temp['data'] + [[
                    float(df['??????'][index]),
                    float(df['??????'][index]),
                    float(df['??????'][index]),
                    float(df['??????'][index]),
                    int(df['?????????'][index])
                ] for index in range(df.shape[0])],
                'volumes': temp['volumes'] + [str(df['?????????'][index]) for index in range(df.shape[0])],
                'other': {
                    'name': ['??????', '??????', '??????', '??????', '??????', '?????????', '?????????', '??????', '?????????', '?????????', '?????????'],
                    'value': {
                        'date': temp['other']['value']['date'] + [str(df['??????'][index]) for index in range(df.shape[0])],
                        'open': temp['other']['value']['open'] + [str(df['??????'][index]) for index in range(df.shape[0])],
                        'close': temp['other']['value']['close'] + [str(df['??????'][index]) for index in range(df.shape[0])],
                        'high': temp['other']['value']['high'] + [str(df['??????'][index]) for index in range(df.shape[0])],
                        'low': temp['other']['value']['low'] + [str(df['??????'][index]) for index in range(df.shape[0])],
                        'volumes': temp['other']['value']['volumes'] + [str(df['?????????'][index]) for index in range(df.shape[0])],
                        'turnover': temp['other']['value']['turnover'] + [str(df['?????????'][index]) for index in range(df.shape[0])],
                        'amplitude': temp['other']['value']['amplitude'] + [str(df['??????'][index]) + '%' for index in range(df.shape[0])],
                        'Chg': temp['other']['value']['Chg'] + [str(df['?????????'][index]) + '%' for index in range(df.shape[0])],
                        'change': temp['other']['value']['change'] + [str(df['?????????'][index]) for index in range(df.shape[0])],
                        'turnover_rate': temp['other']['value']['turnover_rate'] + [str(df['?????????'][index]) + '%' for index in range(df.shape[0])]
                    }
                }
            }
            with open('F:/data/KG_GCN_Stock_price_trend_prediction_system/test/'+stock_code+'.json', 'w') as sf:
                json.dump(history_price, sf)
        except Exception as e:
            print(stock_code, 'error', e)
            error_stock_code.append(stock_code)
        else:
            print(stock_code, 'finish')

        print(round(time.time()-start, 2))
        time.sleep(1)

    print(error_stock_code)


if __name__ == '__main__':
    get_history_price()


