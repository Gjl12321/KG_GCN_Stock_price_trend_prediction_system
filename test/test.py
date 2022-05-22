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


def test():
    df = pd.read_csv('/data/stock_info.csv', index_col=0)
    for i in range(df.shape[0]):
        print(df['名称'][i],
              df['代码'][i],
              df['名称'][i],
              df['行业'][i],
              df['总市值'][i],
              df['流通市值'][i],
              df['总股本'][i],
              df['流通股'][i],
              df['上市时间'][i]
              )


if __name__ == '__main__':
    test()


