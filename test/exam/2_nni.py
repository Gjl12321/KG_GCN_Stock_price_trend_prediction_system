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
from torch.backends import cudnn
from torch.utils.data import DataLoader
from torch.utils.data.dataset import Dataset


EMPTY_DEFAULT = -1.0


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    # cudnn.benchmark = False
    # cudnn.enabled = False
    torch.backends.cudnn.deterministic = True


class MyDataset(Dataset):
    def __init__(self, data, label):
        if isinstance(data, pd.DataFrame):
            self.data = data.values
        elif isinstance(data, np.ndarray):
            self.data = data
        else:
            self.data - np.arrap(data)

        if isinstance(label, pd.Series):
            self.label = label.values
        elif isinstance(label, np.ndarray):
            self.label = label
        else:
            self.label = np.array(label)

    def __len__(self):
        return len(self.label)

    def __getitem__(self, index):
        sample = np.array(self.data[index], dtype=float)
        sample_label = self.label[index]
        return sample, sample_label


class LSTM_model(nn.Module):
    def __init__(self, input_size=4, hidden_size=32, num_layers=1):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            batch_first=True
        )
        self.classifier = nn.Linear(in_features=self.hidden_size, out_features=1)

    def forward(self, x):
        r_out, _ = self.lstm(x)
        output = self.classifier(r_out[:, -1, :])
        return output


class GRU_model(nn.Module):
    def __init__(self, input_size=4, hidden_size=32, num_layers=1):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.GRU = nn.GRU(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            batch_first=True
        )
        self.classifier = nn.Linear(in_features=self.hidden_size, out_features=1)

    def forward(self, x):
        r_out, _ = self.GRU(x)
        output = self.classifier(r_out[:, -1, :])
        return output


def train_step(train_loader, optimizers, model, loss_func):
    model.train()
    epoch_loss, acc, roc_auc, prc = 0, 0, 0, 0
    pred_proba, pred_01, labels = np.array([]), np.array([]), np.array([])

    for _, (batch_x, batch_y) in enumerate(train_loader):
        batch_x = batch_x.float().cuda()
        batch_y = batch_y.float().cuda()

        with torch.set_grad_enabled(True):
            predict = model(batch_x)
            loss = loss_func(predict, batch_y.unsqueeze(1))
            optimizers.zero_grad()
            loss.backward()
            optimizers.step()

        pred_proba = np.concatenate((pred_proba, predict.detach().cpu().numpy().reshape(-1)), axis=0)
        epoch_loss += loss.item() * batch_y.size(0)
        labels = np.concatenate((labels, batch_y.cpu().detach().numpy()), axis=0)
        # print('report_intermediate: ', loss.item())
        # nni.report_intermediate_result(loss.item())

    pred_01 = np.array(list(map(lambda x: 1 if x >= 0.5 else 0, pred_proba)))
    epoch_loss /= len(labels)
    acc = sum(map(lambda x, y: 1 if x == int(y) else 0, pred_01, labels)) * 1.0 / len(labels)
    roc_auc = roc_auc_score(labels, pred_proba)
    precision, recall, thresholds = precision_recall_curve(labels, pred_proba)
    prc = auc(recall, precision)

    return epoch_loss, acc, roc_auc, prc


def test_step(test_loader, model, loss_func):
    model.eval()
    epoch_loss, acc, roc_auc, prc = 0, 0, 0, 0
    pred_proba, pred_01, labels = np.array([]), np.array([]), np.array([])

    for _, (batch_x, batch_y) in enumerate(test_loader):
        batch_x = batch_x.float().cuda()
        batch_y = batch_y.float().cuda()
        with torch.no_grad():
            predict = model(batch_x)
        loss = loss_func(predict, batch_y.unsqueeze(1))
        pred_proba = np.concatenate((pred_proba, predict.detach().cpu().numpy().reshape(-1)), axis=0)
        epoch_loss += loss.item() * batch_y.size(0)
        labels = np.concatenate((labels, batch_y.cpu().detach().numpy()), axis=0)

    pred_01 = np.array(list(map(lambda x: 1 if x >= 0.5 else 0, pred_proba)))
    epoch_loss /= len(labels)
    acc = sum(map(lambda x, y: 1 if x == int(y) else 0, pred_01, np.array(labels, dtype=int))) * 1.0 / len(labels)
    roc_auc = roc_auc_score(labels, pred_proba)
    precision, recall, thresholds = precision_recall_curve(labels, pred_proba)
    prc = auc(recall, precision)

    return epoch_loss, acc, pred_proba, pred_01, labels, roc_auc, prc


def test_step_nni(test_loader, model, loss_func):
    model.eval()
    epoch_loss, acc, roc_auc, prc = 0, 0, 0, 0
    pred_proba, pred_01, labels = np.array([]), np.array([]), np.array([])

    for _, (batch_x, batch_y) in enumerate(test_loader):
        batch_x = batch_x.float().cuda()
        batch_y = batch_y.float().cuda()
        with torch.no_grad():
            predict = model(batch_x)
        loss = loss_func(predict, batch_y.unsqueeze(1))
        pred_proba = np.concatenate((pred_proba, predict.detach().cpu().numpy().reshape(-1)), axis=0)
        epoch_loss += loss.item() * batch_y.size(0)
        labels = np.concatenate((labels, batch_y.cpu().detach().numpy()), axis=0)
        # nni.report_intermediate_result(loss.item())

    pred_01 = np.array(list(map(lambda x: 1 if x >= 0.5 else 0, pred_proba)))
    epoch_loss /= len(labels)
    acc = sum(map(lambda x, y: 1 if x == int(y) else 0, pred_01, np.array(labels, dtype=int))) * 1.0 / len(labels)
    roc_auc = roc_auc_score(labels, pred_proba)
    precision, recall, thresholds = precision_recall_curve(labels, pred_proba)
    prc = auc(recall, precision)
    nni.report_intermediate_result({
        'default': roc_auc,
        'Acc': accuracy_score(labels, pred_01)
    })

    return epoch_loss, acc, pred_proba, pred_01, labels, roc_auc, prc


def cal_one_class_prec_recall(task, y_true, pred_proba):
    task_name, thr = task.split('@')
    if task_name == 'prec':
        task_name_id = 0
    else:
        task_name_id = 1
    thr = int(thr) / 100.0
    precision, recall, thresholds = precision_recall_curve(y_true, pred_proba)
    pre_recall_thd = np.array(list(zip(precision, recall, thresholds)))
    if task_name_id == 0:
        disMinIndex = np.where(pre_recall_thd[:, task_name_id] >= thr)
    else:
        pre_recall_thd = pre_recall_thd[::-1]
        disMinIndex = np.where(pre_recall_thd[:, task_name_id] >= thr)
    if len(disMinIndex[0]) == 0:
        return None, None, None
    else:
        return (pre_recall_thd[disMinIndex[0][0]][0],
                pre_recall_thd[disMinIndex[0][0]][1],
                pre_recall_thd[disMinIndex[0][0]][2])


def dataframe_to_list(input_df):
    res = []
    for i in range(input_df.shape[0]):
        res.append([input_df.features[i], input_df.label[i]])
    return np.array(res)


def preprocess(stock_code, stock_list):
    start_date = params['start_date']
    end_date = params['end_date']

    main_data = ak.stock_zh_a_cdr_daily(symbol=stock_code, start_date=start_date, end_date=end_date)
    data_dict = {}

    min_open, max_open = min(main_data.open.values), max(main_data.open.values)
    min_high, max_high = min(main_data.high.values), max(main_data.high.values)
    min_low, max_low = min(main_data.low.values), max(main_data.low.values)
    min_close, max_close = min(main_data.close.values), max(main_data.close.values)
    for i in range(main_data.shape[0]):
        time_stamp = str(int(time.mktime(time.strptime(str(main_data.date[i]), "%Y-%m-%d"))))
        data_dict[time_stamp] = [
            (main_data.open.values[i] - min_open) / (max_open - min_open),
            (main_data.high.values[i] - min_high) / (max_high - min_high),
            (main_data.low.values[i] - min_low) / (max_low - min_low),
            (main_data.close.values[i] - min_close) / (max_close - min_close)
        ]

    for i in range(len(stock_list)):
        try:
            stock_data = ak.stock_zh_a_cdr_daily(symbol=stock_list[i], start_date=start_date, end_date=end_date)

            min_open, max_open = min(stock_data.open.values), max(stock_data.open.values)
            min_high, max_high = min(stock_data.high.values), max(stock_data.high.values)
            min_low, max_low = min(stock_data.low.values), max(stock_data.low.values)
            min_close, max_close = min(stock_data.close.values), max(stock_data.close.values)
            for j in range(stock_data.shape[0]):
                time_stamp = str(int(time.mktime(time.strptime(str(stock_data.date[j]), "%Y-%m-%d"))))
                if time_stamp in data_dict.keys():
                    data_dict[time_stamp] += [
                        (stock_data.open.values[j] - min_open) / (max_open - min_open),
                        (stock_data.high.values[j] - min_high) / (max_high - min_high),
                        (stock_data.low.values[j] - min_low) / (max_low - min_low),
                        (stock_data.close.values[j] - min_close) / (max_close - min_close)
                    ]
            for k in data_dict.keys():
                while len(data_dict[k]) < 4*(i+2):
                    data_dict[k].append(EMPTY_DEFAULT)
        except:
            print(stock_list[i])

    data_list = [[k, v] for k, v in data_dict.items()]
    data_list = sorted(data_list, key=lambda x: x[0], reverse=False)

    days_for_train = params['days_for_train']
    X_all, Y_all = [], []
    for i in range(len(data_list)-days_for_train):
        tmp = []
        for j in range(i, i+days_for_train):
            tmp.append(data_list[j][1])
        X_all.append(tmp)
        Y_all.append(1 if data_list[i + days_for_train][1][3] >= data_list[i + days_for_train - 1][1][3] else 0)
    X_all, Y_all = np.array(X_all), np.array(Y_all)

    df_all = pd.DataFrame({
        'features': [i for i in X_all],
        'label': [i for i in Y_all]
    })

    setup_seed(params['random_seed'])
    id_idx = list(set(df_all.index))
    train_id_idx = list(random.sample(id_idx, int(len(id_idx) * 0.9)))
    test_id_idx = list(set(id_idx) - set(train_id_idx))
    train_sample = df_all[df_all.index.isin(train_id_idx)].reset_index(drop=True)
    test_sample = df_all[df_all.index.isin(test_id_idx)].reset_index(drop=True)

    train_data = dataframe_to_list(train_sample)
    test_data = dataframe_to_list(test_sample)

    # np.save("train_data.npy", train_data)
    # np.save("test_data.npy", test_data)

    print(Counter(train_sample.label))
    print(Counter(test_sample.label))

    return train_data, test_data


def run(train_sample, test_sample):
    input_sizt = len(train_sample[0][0][0])

    x_train, x_valid, y_train, y_valid = train_test_split(train_sample[:, 0], train_sample[:, 1], test_size=0.1, random_state=params['random_seed'])
    x_test = test_sample[:, 0]
    y_test = test_sample[:, 1]
    print(Counter(y_train), Counter(y_valid), Counter(y_test))

    batch_size = 8
    setup_seed(params['random_seed'])
    train_loader = DataLoader(MyDataset(x_train, y_train), batch_size=batch_size, shuffle=True, drop_last=True)
    valid_loader = DataLoader(MyDataset(x_valid, y_valid), batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(MyDataset(x_test, y_test), batch_size=batch_size, shuffle=False)

    file_dir = 'log'
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)

    EPOCH = params['epoch']
    if params['model_name'] == 'LSTM':
        model = LSTM_model(input_size=input_sizt, hidden_size=params['hidden_size']).cuda()
    elif params['model_name'] == 'GRU':
        model = GRU_model(input_size=input_sizt, hidden_size=params['hidden_size']).cuda()
    else:
        model = LSTM_model(input_size=input_sizt, hidden_size=params['hidden_size']).cuda()

    optimizers = torch.optim.Adam(model.parameters(), lr=params['lr'], weight_decay=params['weight_decay'])
    loss_func = nn.BCEWithLogitsLoss().cuda()

    best_epoch = 1
    min_loss = 100
    early_stop = 0

    for epoch in range(1, EPOCH + 1):
        train_epoch_loss, train_acc, train_roc, train_prc = train_step(train_loader, optimizers, model, loss_func)
        valid_epoch_loss, valid_acc, pred_proba, pred_01, labels, valid_roc, valid_prc = test_step_nni(valid_loader, model,
                                                                                                   loss_func)

        if min_loss > valid_epoch_loss:
            best_epoch = epoch
            min_loss = valid_epoch_loss
            early_stop = 0
        else:
            early_stop += 1

        state = {
            'net': model.state_dict(),
            'optimizer': optimizers.state_dict(),
            'epoch': epoch
        }
        torch.save(state, os.path.join(file_dir, 'model_%d.pt' % epoch))

        if early_stop >= params['early_stop']:
            break

    checkpoint = torch.load(os.path.join(file_dir, 'model_%d.pt' % best_epoch))
    model.load_state_dict(checkpoint['net'])
    optimizers.load_state_dict(checkpoint['optimizer'])
    valid_epoch_loss, valid_acc, pred_proba, pred_01, labels, valid_roc, valid_prc = test_step(valid_loader, model, loss_func)
    # nni.report_final_result({
    #     'default': valid_roc,
    #     'Roc': accuracy_score(labels, pred_01)
    # })
    # test_epoch_loss, test_acc, pred_proba, pred_01, labels, test_roc, test_prc = test_step(test_loader, model, loss_func)

    print('Acc: ', accuracy_score(labels, pred_01), '\tRoc: ', valid_roc)


if __name__ == '__main__':
    # params = nni.get_next_parameter()
    params = {
        'early_stop': 10,
        'weight_decay': 0.01,
        'lr': 0.0001,
        'epoch': 100,
        'hidden_size': 32,
        'batch_size': 32,
        'random_seed': 100,
        'model_name': 'LSTM',
        'end_date': '20191231',
        'start_date': '20130104',
        'days_for_train': 10,
        # 'roc': 0.625,
        # 'acc': 0.4771,
        'stock': 'sh600007'
    }

    stock = params['stock']

    with open('1_record.json', 'r') as rf:
        stock_dict = json.load(rf)
    relate_list = stock_dict[stock]
    relate_list = sorted(relate_list[1:], key=lambda x: x[1], reverse=True)
    max_nums = max([x[1] for x in relate_list])
    max_index = 0
    for i in range(len(relate_list)):
        if relate_list[i][1] < max_nums:
            max_index = i
            break
    relate_stocks = [x[0] for x in relate_list[:max_index]]

    train_data, test_data = preprocess(stock, relate_stocks)

    run(train_data, test_data)


