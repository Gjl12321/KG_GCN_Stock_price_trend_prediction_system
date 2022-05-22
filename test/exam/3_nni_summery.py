import os
import json
import numpy as np
import pandas as pd


if __name__ == '__main__':
    root_path = 'C:/Users/admin/nni-experiments/Z8Vxrtle/trials'

    stock = []
    days_for_train = []
    model_name = []
    random_seed = []
    batch_size = []
    hidden_size = []
    lr = []
    weight_decay = []
    roc = []

    for file in os.listdir(root_path):
        try:
            params_path = root_path + '/' + file + '/parameter.cfg'
            roc_path = root_path + '/' + file + '/.nni/metrics'


            with open(roc_path, 'r') as rf:
                temp = rf.readlines()
            result = json.loads(str('{' + temp[-1][:-1].split('{')[1]))['value']

            with open(params_path, 'r') as rf:
                temp = json.loads(str(rf.read()))
            params = temp['parameters']

            stock.append(params['stock'])
            days_for_train.append(params['days_for_train'])
            model_name.append(params['model_name'])
            random_seed.append(params['random_seed'])
            batch_size.append(params['batch_size'])
            hidden_size.append(params['hidden_size'])
            lr.append(params['lr'])
            weight_decay.append(params['weight_decay'])
            roc.append(result)
        except:
            print(file)

    df = pd.DataFrame({
        'stock': stock,
        'days_for_train': days_for_train,
        'model_name': model_name,
        'random_seed': random_seed,
        'batch_size': batch_size,
        'hidden_size': hidden_size,
        'lr': lr,
        'weight_decay': weight_decay,
        'roc': roc
    })
    df = df.sort_values(by=['stock', 'model_name', 'roc'], ascending=False).drop_duplicates(subset=['stock', 'model_name'], keep='first')
    df.reset_index(inplace=True, drop=True)
    print(df)
