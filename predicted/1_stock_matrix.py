import time
import json
import numpy as np
import pandas as pd
import akshare as ak
from py2neo import Graph, Node, Relationship, cypher
from selenium import webdriver
from pyquery import PyQuery as pq
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


graph = Graph("bolt://localhost:7687", auth=("neo4j", "gjl19971213"))
stocks = graph.run("match (a:Stock) return a").data()

stock_dict = {}
for i in range(len(stocks)):
    stock_dict[stocks[i]['a']['代码']] = i

stock_list = list(stock_dict.keys())

matrix = [[0 for i in stock_dict.keys()] for j in stock_dict.keys()]

for i in range(len(stock_list)):
    start_time = time.time()
    print(i+1, '/', len(stock_list), end='\t')
    sum = 0
    for j in range(i+1, len(stock_list)):
        sign = False

        if len(graph.run("match data=(a:Stock{代码:'"+stock_list[i]+"'})-[]-(c:Industry)-[]-(b:Stock{代码:'"+stock_list[j]+"'}) return data").data()) > 0:
            matrix[stock_dict[stock_list[i]]][stock_dict[stock_list[j]]] += graph.run("match (a:Stock{代码:'sz000969'})-[r1]-(c:Industry)-[r2]-(b:Stock{代码:'sz002824'}) return (toFloat(r1.weight)+toFloat(r2.weight))/100 as data").data()[0]['data']
            matrix[stock_dict[stock_list[j]]][stock_dict[stock_list[i]]] += graph.run("match (a:Stock{代码:'sz000969'})-[r1]-(c:Industry)-[r2]-(b:Stock{代码:'sz002824'}) return (toFloat(r1.weight)+toFloat(r2.weight))/100 as data").data()[0]['data']
            sign = True
        if len(graph.run("match (a:Stock{代码:'"+stock_list[i]+"'})-[]-(c:Concept)-[]-(b:Stock{代码:'"+stock_list[j]+"'}) return c.name").data()) > 0:
            for concept in graph.run("match (a:Stock{代码:'"+stock_list[i]+"'})-[]-(c:Concept)-[]-(b:Stock{代码:'"+stock_list[j]+"'}) return c.name as data").data():
                concept_name = concept['data']
                matrix[stock_dict[stock_list[i]]][stock_dict[stock_list[j]]] += 2 / graph.run("match (a:Stock)-[r1]-(c:Concept{name:'"+concept_name+"'}) return count(a) as data").data()[0]['data']
                matrix[stock_dict[stock_list[j]]][stock_dict[stock_list[i]]] += 2 / graph.run("match (a:Stock)-[r1]-(c:Concept{name:'"+concept_name+"'}) return count(a) as data").data()[0]['data']
            sign = True
        if len(graph.run("match (a:Stock{代码:'"+stock_list[i]+"'})-[]-(c:Shareholder)-[]-(b:Stock{代码:'"+stock_list[j]+"'}) return c.name").data()) > 0:
            for shareholder in graph.run("match (a:Stock{代码:'"+stock_list[i]+"'})-[]-(c:Shareholder)-[]-(b:Stock{代码:'"+stock_list[j]+"'}) return c.name as data").data():
                shareholder_name = shareholder['data']
                matrix[stock_dict[stock_list[i]]][stock_dict[stock_list[j]]] += 2 / graph.run("match (a:Stock)-[r1]-(c:Shareholder{name:'"+shareholder_name+"'}) return count(a) as data").data()[0]['data']
                matrix[stock_dict[stock_list[j]]][stock_dict[stock_list[i]]] += 2 / graph.run("match (a:Stock)-[r1]-(c:Shareholder{name:'"+shareholder_name+"'}) return count(a) as data").data()[0]['data']
            sign = True

        if sign:
            sum += 1
            matrix[stock_dict[stock_list[i]]][stock_dict[stock_list[j]]] = min(1000.0, round(float(
                1 / matrix[stock_dict[stock_list[i]]][stock_dict[stock_list[j]]])), 6)
            matrix[stock_dict[stock_list[j]]][stock_dict[stock_list[i]]] = min(1000.0, round(float(
                1 / matrix[stock_dict[stock_list[j]]][stock_dict[stock_list[i]]])), 6)
    print(sum, '\t', time.time() - start_time)


with open('data/stock_matrix_relation.json', 'w') as sf:
    json.dump({'stock_dict': stock_dict, 'stock_matrix': matrix}, sf)
