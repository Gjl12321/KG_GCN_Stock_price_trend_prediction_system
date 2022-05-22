import json

with open('1_record.txt', 'r') as rf:
    temp = rf.readlines()

stock_list = {}
for i in temp:
    stock_list[json.loads(str(i[:-1]).replace('\'', '"'))[0][0]] = json.loads(str(i[:-1]).replace('\'', '"'))[1:]

with open('1_record.json', 'w') as sf:
    json.dump(stock_list, sf)

