import os
import re
import json
import paramiko
import pandas as pd


def get_model_params():
    hostname = "120.46.158.255"
    port = 22
    username = "root"
    password = "GJLgjl_19971213"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, username, password, compress=True)
    sftp_client = client.open_sftp()

    early_stop = []
    weight_decay = []
    lr = []
    epoch = []
    hidden_size = []
    batch_size = []
    random_seed = []
    model_name = []
    end_date = []
    start_date = []
    days_for_train = []
    stock = []
    roc = []
    acc = []

    cnt = 0

    for root_path in ['/root/nni-experiments/r2fENBIg/trials', '/root/nni-experiments/hJqwCFOV/trials']:
        for file_path in sftp_client.listdir(root_path):
            cnt += 1

            with sftp_client.open(root_path + '/' + file_path + '/parameter.cfg', 'r') as rf:
                temp = rf.read()
            pattern = r'"parameters": {"early_stop": (.+), "weight_decay": (.+), "lr": (.+), "epoch": (.+), "hidden_size": (.+), "batch_size": (.+), "random_seed": (.+), "model_name": "(.+)", "end_date": "(.+)", "start_date": "(.+)", "days_for_train": (.+), "stock": "(.+)"}'
            result = re.search(pattern, str(temp))

            early_stop.append(result.groups()[0])
            weight_decay.append(result.groups()[1])
            lr.append(result.groups()[2])
            epoch.append(result.groups()[3])
            hidden_size.append(result.groups()[4])
            batch_size.append(result.groups()[5])
            random_seed.append(result.groups()[6])
            model_name.append(result.groups()[7])
            end_date.append(result.groups()[8])
            start_date.append(result.groups()[9])
            days_for_train.append(result.groups()[10])
            stock.append(result.groups()[11])

            with sftp_client.open(root_path + '/' + file_path + '/.nni/metrics', 'r') as rf:
                temp = rf.read()
            roc.append(float(str(temp).split('"{\\\\"default\\\\": ')[-1].split(', \\\\"accuracy\\\\"')[0]))
            acc.append(float(str(temp).replace('}"}\\n\'', '').split('\\\\"accuracy\\\\": ')[-1]))

            if cnt % 1000 == 1:
                print(cnt, '/ 152789')
                pd.DataFrame({
                    'early_stop': early_stop,
                    'weight_decay': weight_decay,
                    'lr': lr,
                    'epoch': epoch,
                    'hidden_size': hidden_size,
                    'batch_size': batch_size,
                    'random_seed': random_seed,
                    'model_name': model_name,
                    'end_date': end_date,
                    'start_date': start_date,
                    'days_for_train': days_for_train,
                    'stock': stock,
                    'roc': roc,
                    'acc': acc
                }).to_csv('temp.csv')

    df = pd.DataFrame({
        'early_stop': early_stop,
        'weight_decay': weight_decay,
        'lr': lr,
        'epoch': epoch,
        'hidden_size': hidden_size,
        'batch_size': batch_size,
        'random_seed': random_seed,
        'model_name': model_name,
        'end_date': end_date,
        'start_date': start_date,
        'days_for_train': days_for_train,
        'stock': stock,
        'roc': roc,
        'acc': acc
    })
    df.to_csv('temp.csv')


def save_model_params():
    df = pd.read_csv('temp.csv', index_col=0)
    df = df.sort_values(by=['stock', 'model_name', 'roc'], ascending=False).drop_duplicates(subset=['stock'],
                                                                                            keep='first')
    df.reset_index(inplace=True, drop=True)

    model_dict = {}
    for index in range(df.shape[0]):
        model_dict[df['stock'][index]] = {
            'early_stop': 10,
            'weight_decay': float(df['weight_decay'][index]),
            'lr': float(df['lr'][index]),
            'epoch': 100,
            'hidden_size': int(df['hidden_size'][index]),
            'batch_size': 32,
            'random_seed': int(df['random_seed'][index]),
            'model_name': df['model_name'][index],
            'end_date': '20191231',
            'start_date': '20130104',
            'days_for_train': int(df['days_for_train'][index]),
            'roc': round(float(df['roc'][index]), 4),
            'acc': round(float(df['acc'][index]), 4)
        }
    print(model_dict)
    with open('stock_params.json', 'w') as sf:
        json.dump(model_dict, sf)


if __name__ == '__main__':

    df_root = pd.read_csv('temp.csv', index_col=0)

    df = df_root.sort_values(by=['stock', 'model_name', 'acc'], ascending=False).drop_duplicates(subset=['stock'], keep='first')
    df.reset_index(inplace=True, drop=True)
    data = list(df['acc'])
    print(sum(data)/len(data))
    # for i in range(df.shape[0]):
    #     data[df['stock'][i]] = [round(df['roc'][i], 6)]
    #
    # df = df_root.sort_values(by=['stock', 'model_name', 'acc'], ascending=False).drop_duplicates(subset=['stock'], keep='first')
    # df.reset_index(inplace=True, drop=True)
    # for i in range(df.shape[0]):
    #     data[df['stock'][i]] += [round(df['acc'][i], 6)]
    #
    # data = [
    #     [
    #         k,
    #         data[k][0],
    #         data[k][1]
    #     ] for k in data.keys()
    # ]
    # data = sorted(data, key=lambda x: x[1], reverse=True)
    # print(data)

    # df = df_root.query('days_for_train == 20').sort_values(by=['stock', 'model_name', 'acc'], ascending=False).drop_duplicates(subset=['stock'], keep='first')
    # df.reset_index(inplace=True, drop=True)
    # print(round(sum(df['acc']) / len(df['acc']), 4))
    # for i in range(df.shape[0]):
    #     data[df['stock'][i]] = [round(df['acc'][i], 6)]
    #
    # data = [
    #     [
    #         k,
    #         data[k][0],
    #         data[k][1]
    #     ] for k in data.keys()
    # ]
    # data = sorted(data, key=lambda x: x[1], reverse=True)
    # print(data)


    # with open('stock_params.json', 'r') as sf:
    #     temp = json.load(sf)
    # data = [
    #     [
    #         k,
    #         temp[k]['acc'],
    #         temp[k]['roc'],
    #     ] for k in temp.keys()
    # ]
    # # print(data)
    # res = []
    # for k in temp.keys():
    #     res.append(temp[k]['acc'])
    # print(max(res), sum(res)/len(res))

    print()
