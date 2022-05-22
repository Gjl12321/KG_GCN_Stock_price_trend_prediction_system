import numpy as np
import scipy.sparse as sp
import torch
import networkx as nx


def normalize(mx):
    """Row-normalize sparse matrix"""
    rowsum = np.array(mx.sum(1), dtype=np.float32)
    r_inv = np.power(rowsum, -1).flatten()
    r_inv[np.isinf(r_inv)] = 0.
    r_mat_inv = sp.diags(r_inv)
    mx = r_mat_inv.dot(mx)
    return mx


def mx_to_sparse_tensor(mx):
    """Convert a scipy sparse matrix to a torch sparse tensor."""
    mx = mx.tocoo().astype(np.float32)
    indices = torch.from_numpy(np.vstack((mx.row, mx.col)).astype(np.int64))
    values = torch.from_numpy(mx.data)
    shape = torch.Size(mx.shape)
    return torch.sparse.FloatTensor(indices, values, shape)


def load_data(G):
    """Load network (graph)"""
    adj = nx.to_scipy_sparse_matrix(G).tocoo()
    adj = normalize(adj+sp.eye(adj.shape[0]))
    adj = mx_to_sparse_tensor(adj)
    features = torch.eye(len(G.nodes())).to_sparse()
    return adj, features


def get_max_index(nums):
    res = 0
    for i in range(len(nums)):
        if nums[i] > nums[res]:
            res = i
    return res
