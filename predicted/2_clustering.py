import os
import math
import json
import torch
import random
import sklearn
import numpy as np
import networkx as nx
import torch.nn as nn
import scipy.sparse as sp
import torch.optim as optim
import torch.nn.functional as F
from collections import defaultdict, Counter
from torch.nn.parameter import Parameter
from tools import load_data, get_max_index
from model import GCNClusterNet, GCN, GraphConvolution, cluster


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


# 损失函数
def loss_modularity(r, bin_adj, mod):
    bin_adj_nodiag = bin_adj * (torch.ones(bin_adj.shape[0], bin_adj.shape[0]) - torch.eye(bin_adj.shape[0]))
    return (1. / bin_adj_nodiag.sum()) * (r.t() @ mod @ r).trace()


# 获得模块度矩阵
def make_modularity_matrix(adj):
    adj = adj * (torch.ones(adj.shape[0], adj.shape[0]) - torch.eye(adj.shape[0]))
    degrees = adj.sum(dim=0).unsqueeze(1)
    mod = adj - degrees @ degrees.t() / adj.sum()
    return mod


def save_matrix():
    with open('F:/python_project/stock/data/stock_matrix_relation.json', 'r') as rf:
        text = json.load(rf)

    stock_dist = text['stock_dict']
    stock_matrix_all = text['stock_matrix']
    stocks = [
            'sh600004', 'sh600007', 'sh600009', 'sh600011', 'sh600012', 'sh600015', 'sh600016', 'sh600017', 'sh600028', 'sh600033', 'sh600085', 'sh600111', 'sh600123', 'sh600159', 'sh600192', 'sh600197', 'sh600213', 'sh600235', 'sh600261', 'sh600262', 'sh600269', 'sh600298', 'sh600302', 'sh600320', 'sh600322', 'sh600361', 'sh600377', 'sh600456', 'sh600495', 'sh600508', 'sh600519', 'sh600560', 'sh600563', 'sh600573', 'sh600583', 'sh600586', 'sh600600', 'sh600616', 'sh600642', 'sh600650', 'sh600660', 'sh600662', 'sh600684', 'sh600692', 'sh600712', 'sh600742', 'sh600805', 'sh600808', 'sh600820', 'sh600824', 'sh600838', 'sh600854', 'sh600897', 'sh600971', 'sh600992', 'sh600993', 'sh601038', 'sh601098', 'sh601177', 'sh601179', 'sh601288', 'sh601328', 'sh601333', 'sh601398', 'sh601601', 'sh601607', 'sh601666', 'sh601668', 'sh601677', 'sh601800', 'sh601808', 'sh601898', 'sh601939', 'sh601958', 'sh601988', 'sh603000', 'sh603167', 'sz000011', 'sz000014', 'sz000027', 'sz000088', 'sz000528', 'sz000548', 'sz000550', 'sz000554', 'sz000561', 'sz000570', 'sz000637', 'sz000702', 'sz000722', 'sz000731', 'sz000759', 'sz000789', 'sz000830', 'sz000848', 'sz000869', 'sz000880', 'sz000886', 'sz000915', 'sz000919', 'sz000951', 'sz000966', 'sz000983', 'sz000985', 'sz002028', 'sz002041', 'sz002066', 'sz002083', 'sz002095', 'sz002096', 'sz002179', 'sz002187', 'sz002204', 'sz002222', 'sz002232', 'sz002262', 'sz002294', 'sz002304', 'sz002362', 'sz002365', 'sz002372', 'sz002393', 'sz002394', 'sz002419', 'sz002457', 'sz002463', 'sz002484', 'sz002561', 'sz002641', 'sz002646', 'sz300024', 'sz300105', 'sz300127', 'sz300204', 'sz300258', 'sz300321', 'sz300333', 'sz300354', 'sh600064', 'sh600101', 'sh600108', 'sh600272', 'sh600276', 'sh600316', 'sh600371', 'sh600505', 'sh600668', 'sh600674', 'sh600783', 'sh600801', 'sh600830', 'sh601318', 'sh601339', 'sh601628', 'sh601857', 'sh601880', 'sh603366', 'sz000049', 'sz000419', 'sz000423', 'sz000596', 'sz000623', 'sz000680', 'sz000823', 'sz000888', 'sz002032', 'sz002039', 'sz002315', 'sz002595', 'sz300033', 'sh600031', 'sh600067', 'sh600178', 'sh600188', 'sh600305', 'sh600307', 'sh600348', 'sh600383', 'sh600386', 'sh600425', 'sh600449', 'sh600548', 'sh600611', 'sh600618', 'sh600720', 'sh600776', 'sh600802', 'sh600833', 'sh600837', 'sh601006', 'sh601188', 'sh601998', 'sz000001', 'sz000039', 'sz000059', 'sz000089', 'sz000096', 'sz000631', 'sz000632', 'sz000652', 'sz000726', 'sz000819', 'sz000822', 'sz002142', 'sz002154', 'sz002275', 'sz002300', 'sz002391', 'sz002420', 'sz300107', 'sz300172', 'sz300305', 'sh600020', 'sh600029', 'sh600060', 'sh600125', 'sh600507', 'sh600612', 'sh600630', 'sh600638', 'sh600823', 'sh600895', 'sh600969', 'sh601117', 'sh601126', 'sh601890', 'sz000402', 'sz000572', 'sz000729', 'sz000767', 'sz000809', 'sz000898', 'sz000988', 'sz002038', 'sz002133', 'sz002144', 'sz002490', 'sz002550', 'sz300206', 'sh600166', 'sh600367', 'sh600635', 'sh600779', 'sh600791', 'sh600885', 'sh601008', 'sh601515', 'sh601678', 'sz000151', 'sz000338', 'sz000581', 'sz000589', 'sz002424', 'sz002448', 'sz002493', 'sz300246', 'sz300327', 'sh600130', 'sh600169', 'sh600210', 'sh600216', 'sh600268', 'sh600326', 'sh600467', 'sh600486', 'sh600761', 'sh600835', 'sh600861', 'sh601139', 'sh601166', 'sh601208', 'sh601636', 'sz000417', 'sz000573', 'sz000965', 'sz000970', 'sz002067', 'sz002138', 'sz002267', 'sz002271', 'sz002287', 'sz002327', 'sz002444', 'sz002508', 'sz002541', 'sz002588', 'sz002618', 'sz002653', 'sz002687', 'sz300039', 'sz300171', 'sz300286', 'sh600027', 'sh600038', 'sh600098', 'sh600118', 'sh600183', 'sh600220', 'sh600409', 'sh600613', 'sh600755', 'sh600883', 'sh601007', 'sz000400', 'sz000598', 'sz000776', 'sz000780', 'sz002234', 'sz002690', 'sh600048', 'sh600059', 'sh600119', 'sh600426', 'sh600874', 'sh601158', 'sh601186', 'sh601555', 'sh601688', 'sz000026', 'sz000157', 'sz000686', 'sz000937', 'sz002007', 'sz002056', 'sz002236', 'sz002397', 'sz002585', 'sz002613', 'sz002666', 'sh600184', 'sh600218', 'sh600223', 'sh600308', 'sh600362', 'sh600391', 'sh600403', 'sh600415', 'sh600470', 'sh600476', 'sh600536', 'sh600585', 'sh600836', 'sh600846', 'sh600999', 'sh601009', 'sh601788', 'sz000030', 'sz000559', 'sz000725', 'sz002023', 'sz002136', 'sz002277', 'sz002428', 'sz002495', 'sz002521', 'sz300210', 'sz300314', 'sh600082', 'sh600343', 'sh600493', 'sh600961', 'sh601106', 'sh601233', 'sh601616', 'sh601929', 'sh601965', 'sz000404', 'sz000488', 'sz000738', 'sz002042', 'sz002258', 'sz300139', 'sh600039', 'sh600054', 'sh600190', 'sh600327', 'sh600345', 'sh600350', 'sh600372', 'sh600513', 'sh600527', 'sh600549', 'sh600596', 'sh600665', 'sh600717', 'sh600789', 'sh600863', 'sh600976', 'sh601002', 'sh601238', 'sh601718', 'sz000552', 'sz000921', 'sz002117', 'sz002186', 'sz002218', 'sz002307', 'sz002311', 'sz002500', 'sz002594', 'sz002615', 'sz002623', 'sz002644', 'sz002658', 'sz300193', 'sz300202', 'sz300264', 'sz300270', 'sh600030', 'sh600036', 'sh600081', 'sh600131', 'sh600138', 'sh600325', 'sh600360', 'sh600463', 'sh600535', 'sh600841', 'sh601010', 'sh601107', 'sh601818', 'sz000785', 'sz000933', 'sz002243', 'sz002244', 'sz002540', 'sz002634', 'sz300245', 'sz300307', 'sh600176', 'sh600249', 'sh600436', 'sh600459', 'sh600809', 'sh600812', 'sh600826', 'sh601566', 'sz000060', 'sz002068', 'sz002250', 'sz002472', 'sz300042', 'sz300275', 'sh600439', 'sh600491', 'sh600501', 'sh600594', 'sh600624', 'sh600658', 'sh600697', 'sh600787', 'sh600831', 'sh601222', 'sh601231', 'sh601377', 'sz000055', 'sz000541', 'sz000667', 'sz000922', 'sz002024', 'sz002029', 'sz002087', 'sz002158', 'sz002182', 'sz002281', 'sz002380', 'sz002536', 'sz002563', 'sz300124', 'sh600115', 'sh600132', 'sh600329', 'sh600435', 'sh600743', 'sh600998', 'sz000735', 'sz002001', 'sz002105', 'sz002118', 'sz002202', 'sz002241', 'sz002342', 'sz002430', 'sz300147', 'sz300218', 'sh600008', 'sh600300', 'sh600509', 'sh600518', 'sh600557', 'sh600706', 'sh600718', 'sh601116', 'sh601218', 'sh601588', 'sh601933', 'sh601991', 'sh603002', 'sz000507', 'sz000783', 'sz000859', 'sz000895', 'sz000957', 'sz000993', 'sz002017', 'sz002064', 'sz002140', 'sz002185', 'sz002216', 'sz002695', 'sh600279', 'sh600865', 'sh601099', 'sz000078', 'sz000910', 'sz002237', 'sz002332', 'sz002363', 'sz300231', 'sz300303', 'sh600196', 'sh600266', 'sh600292', 'sh600368', 'sh600376', 'sh600588', 'sh600774', 'sh601908', 'sh603001', 'sz000425', 'sz000800', 'sz000856', 'sz000897', 'sz002008', 'sz002205', 'sz002253', 'sz002501', 'sz300015', 'sh600079', 'sh600089', 'sh600479', 'sh600521', 'sh601011', 'sz000530', 'sz000568', 'sz000685', 'sz000768', 'sz002593', 'sz002603', 'sz002700', 'sh600199', 'sh600251', 'sh600252', 'sh600489', 'sh600496', 'sh600601', 'sh600737', 'sh601699', 'sz002556', 'sz002673', 'sz002689', 'sz300082', 'sh600104', 'sh600352', 'sh601311', 'sz000501', 'sz000525', 'sz000949', 'sz002062', 'sz002284', 'sz002475', 'sz002487', 'sz002698', 'sh600135', 'sh600170', 'sh600310', 'sh600336', 'sh600405', 'sh600567', 'sh600683', 'sh600713', 'sh600726', 'sh600815', 'sh600884', 'sh600894', 'sh601111', 'sh601801', 'sz000777', 'sz000816', 'sz000877', 'sz002035', 'sz002054', 'sz002107', 'sz002627', 'sh600114', 'sh600128', 'sh600311', 'sh600340', 'sh600388', 'sh600816', 'sh603993', 'sz000021', 'sz000701', 'sz002206', 'sz002208', 'sz002293', 'sz002334', 'sz002378', 'sz002402', 'sz002496', 'sz002674', 'sh600121', 'sh600160', 'sh600283', 'sh601258', 'sh601633', 'sz000521', 'sz000551', 'sz000758', 'sz002422', 'sz300079', 'sz300259', 'sh600109', 'sh600185', 'sh600531', 'sh600543', 'sz000728', 'sz002318', 'sz002351', 'sz002406', 'sz002467', 'sz002533', 'sz002648', 'sz300154', 'sz300329', 'sh600056', 'sh600116', 'sh600716', 'sh600851', 'sh601336', 'sz000909', 'sz002333', 'sz002572', 'sz002609', 'sh600037', 'sh600077', 'sh600080', 'sh600500', 'sh600622', 'sh600703', 'sh600731', 'sh600889', 'sz000012', 'sz000420', 'sz000705', 'sz000761', 'sz002433', 'sz300106', 'sz300138', 'sz300304', 'sh600095', 'sh600382', 'sh600523', 'sh601992', 'sz000430', 'sz002078', 'sz002135', 'sz002227', 'sz002242', 'sz002364', 'sz300115', 'sz300175', 'sz300274', 'sh600201', 'sh600676', 'sh600741', 'sh600748', 'sh600887', 'sz000597', 'sz000599', 'sz000961', 'sz002060', 'sz002093', 'sz002146', 'sz002177', 'sz002285', 'sz002488', 'sz002518', 'sz002628', 'sz300217', 'sz300255', 'sh600156', 'sh600281', 'sh600693', 'sh600868', 'sz000620', 'sz000661', 'sz000791', 'sz000875', 'sz002058', 'sz002229', 'sz002494', 'sz002562', 'sz300021', 'sz300155', 'sh600287', 'sh600351', 'sh600537', 'sh600792', 'sh601199', 'sh601899', 'sz000539', 'sz000733', 'sz002385', 'sz300205', 'sz300302', 'sh600066', 'sh600285', 'sh600477', 'sh600980', 'sh601886', 'sz000025', 'sz000543', 'sz000732', 'sz000797', 'sz002274', 'sz002597', 'sh600814', 'sh601058', 'sz000913', 'sz002139', 'sh600000', 'sh600231', 'sh600333', 'sh600337', 'sh600550', 'sh600853', 'sz000532', 'sz000753', 'sz000792', 'sz002022', 'sz002245', 'sz002480', 'sz002489', 'sz002522', 'sz002531', 'sz002539', 'sz002543', 'sz002590', 'sh600839', 'sz002254', 'sz002498', 'sz002546', 'sz002614', 'sz300215', 'sh600180', 'sh600267', 'sh600526', 'sh600562', 'sz000926', 'sz002516', 'sz300119', 'sz300211'
        ]

    stock_matrix = []
    for stock in stocks:
        stock_matrix.append([stock_matrix_all[stock_dist[stock]][stock_dist[j]] for j in stocks])

    # print(len(stock_matrix), len(stock_matrix[0]))

    for stock in stocks:
        params = {
            'stock_code': stock,
            'no_cuda': True,                    # Disables CUDA training
            'seed': 24,                         # Random seed
            'lr': 0.001,                        # Initial learning rate
            'weight_decay': 5e-4,               # Weight decay (L2 loss on parameters)
            'hidden': 128,                      # Number of hidden units
            'embed_dim': 128,                   # Dimensionality of node embeddings
            'dropout': 0.3,                     # Dropout rate (1 - keep probability)
            'K': 4,                             # How many partitions
            'clustertemp': 100,                 # how hard to make the softmax for the cluster assignments
            'train_iters': 300,                 # number of training iterations
            'num_cluster_iter': 1,              # number of iterations for clustering
            'threshold_all': 0.15,
            'threshold': 0.2
        }

        stock_index = stock_dist[params['stock_code']]
        stock_code_list_all = [i for i in stock_dist.keys()]
        stock_code_list = []
        stock_index_list = []

        nums = stock_matrix_all[stock_index]
        name = stock_code_list_all
        n = len(nums)

        for i in range(n-1):
            min_ = i
            for j in range(i+1, n):
                if nums[min_] > nums[j]:
                    min_ = j
            tmp_nums = nums[i]
            tmp_name = name[i]
            nums[i] = nums[min_]
            name[i] = name[min_]
            nums[min_] = tmp_nums
            name[min_] = tmp_name
        # print(nums[-80:])
        # print(name[-80:])

        if n > 80:
            params['threshold_all'] = nums[-80]
            params['threshold'] = nums[-20]
        elif 10 < n <= 80:
            params['threshold_all'] = nums[-(n//3*2)]
            params['threshold'] = nums[-(n//3)]
        elif n <= 10:
            print(stock_code_list_all)
            with open('1_record.txt', 'a') as af:
                af.write(str(stock_code_list_all)+'\n')
            continue

        for i in range(len(stock_matrix_all[stock_index])):
            if stock_matrix_all[stock_index][i] > params['threshold_all']:
                stock_index_list.append(i)
                stock_code_list.append(stock_code_list_all[i])

        matrix = []
        for row in [stock_index] + stock_index_list:
            matrix.append([stock_matrix_all[row][j] for j in [stock_index] + stock_index_list])

        stock_code = [params['stock_code']] + stock_code_list

        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if matrix[i][j] > params['threshold']:
                    matrix[i][j] = 1
                else:
                    matrix[i][j] = 0

        matrix = np.array(matrix)

        relate_stocks = []
        for K in [2, 3, 4, 5]:
            for seed in [10, 20, 100, 200, 1000]:
                G = nx.from_numpy_matrix(np.array(matrix))
                adj_all, features = load_data(G=G)
                bin_adj_all = (adj_all.to_dense() > 0).float()
                test_object = make_modularity_matrix(bin_adj_all)
                model_cluster = GCNClusterNet(nfeat=features.shape[1], nhid=params['hidden'], nout=params['embed_dim'],
                                              dropout=params['dropout'], K=params['K'], cluster_temp=params['clustertemp'])
                optimizer = optim.Adam(model_cluster.parameters(), lr=params['lr'], weight_decay=params['weight_decay'])

                params['K'] = K

                setup_seed(seed)
                losses = []
                losses_test = []
                curr_test_loss = 0.0
                r = []

                best_train_val = 100
                for t in range(1, params['train_iters'] + 1):
                    mu, r, embeds, dist = model_cluster(features, adj_all, params['num_cluster_iter'])
                    loss = loss_modularity(r, bin_adj_all, test_object)
                    loss = -loss
                    optimizer.zero_grad()
                    loss.backward()

                    if t % 10 == 1:
                        r = torch.softmax(100 * r, dim=1)
                        loss_test = loss_modularity(r, bin_adj_all, test_object)
                        if loss.item() < best_train_val:
                            best_train_val = loss.item()
                            curr_test_loss = loss_test.item()

                    losses.append(loss.item())
                    optimizer.step()

                result = [[round(float(i), 6) for i in j] for j in r]

                clusters = defaultdict(int)
                same_class = []
                main_class = get_max_index(result[0])
                for i in range(len(result)):
                    if get_max_index(result[i]) == main_class:
                        same_class.append(i)
                    clusters[get_max_index(result[i])] += 1

                relate_stocks += same_class

        # print(Counter(relate_stocks))

        relate_stocks_result = [[stock_code[k], v] for k, v in Counter(relate_stocks).items()]

        print(relate_stocks_result)
        with open('record.txt', 'a') as af:
            af.write(str(relate_stocks_result)+'\n')


def trans_matrix():
    with open('record.txt', 'r') as rf:
        temp = rf.readlines()

    stock_list = {}
    for i in temp:
        stock_list[json.loads(str(i[:-1]).replace('\'', '"'))[0][0]] = json.loads(str(i[:-1]).replace('\'', '"'))[1:]

    with open('record.json', 'w') as sf:
        json.dump(stock_list, sf)


if __name__ == '__main__':
    save_matrix()
    trans_matrix()
