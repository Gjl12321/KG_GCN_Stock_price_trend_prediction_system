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
from selenium.webdriver.common.action_chains import ActionChains


def get_class_1():
    class_urls = {
        '美容护理': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_770000',
        '环保': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_760000',
        '石油石化': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_750000',
        '煤炭': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000',
        '通信': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_730000',
        '传媒': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_720000',
        '计算机': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_710000',
        '国防军工': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_650000',
        '机械设备': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_640000',
        '电力设备': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_630000',
        '建筑装饰': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_620000',
        '建筑材料': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_610000',
        '综合': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_510000',
        '非银金融': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_490000',
        '银行': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_480000',
        '社会服务': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_460000',
        '商贸零售': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_450000',
        '房地产': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_430000',
        '交通运输': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_420000',
        '公用事业': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_410000',
        '医药生物': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_370000',
        '轻工制造': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_360000',
        '纺织服饰': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_350000',
        '食品饮料': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_340000',
        '家用电器': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_330000',
        '汽车': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_280000',
        '电子': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_270000',
        '有色金属': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_240000',
        '钢铁': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_230000',
        '基础化工': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_220000',
        '农林牧渔': 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_110000'
    }
    browser = webdriver.Chrome()
    class_stock = {}

    for name, url in class_urls.items():
        try:
            browser.get(url)
            time.sleep(1)
            class_stock[name] = []
            if browser.find_element(by=By.XPATH, value='//*[@id="list_pages_top2"]').text == '':
                print('1')
                time.sleep(1)
                codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                for item in codes:
                    if len(item.text.split(' ')) > 2:
                        class_stock[name].append(item.text.split(' ')[:2])
            else:
                print('n')
                while True:
                    time.sleep(1)
                    codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                    for item in codes:
                        if len(item.text.split(' ')) > 2:
                            class_stock[name].append(item.text.split(' ')[:2])
                    next_page = browser.find_element(by=By.XPATH,
                                                     value='/html/body/div[3]/div[5]/div[3]/div[3]/div/a[last()]')
                    if next_page.text == '下一页':
                        next_page.click()
                        continue
                    else:
                        break
        except:
            print(name, url, 'error')
        else:
            print(name, url, 'finish')
    with open('申万一级类别.json', 'w') as sf:
        json.dump(class_stock, sf)


def get_class_2():
    class_names = [
        '通信设备', '通信服务', '电视广播Ⅱ', '出版', '数字媒体', '影视院线', '广告营销', '游戏Ⅱ', '软件开发', 'IT服务Ⅱ',
        '计算机设备', '军工电子Ⅱ', '航海装备Ⅱ', '地面兵装Ⅱ', '航空装备Ⅱ', '航天装备Ⅱ', '自动化设备', '工程机械',
        '轨交设备Ⅱ', '专用设备', '通用设备', '电网设备', '电池', '风电设备', '光伏设备', '其他电源设备Ⅱ', '电机Ⅱ',
        '工程咨询服务Ⅱ', '专业工程', '基础建设', '装修装饰Ⅱ', '房屋建设Ⅱ', '装修建材', '玻璃玻纤', '水泥', '综合Ⅱ',
        '多元金融', '保险Ⅱ', '证券Ⅱ', '农商行Ⅱ', '城商行Ⅱ', '股份制银行Ⅱ', '国有大型银行Ⅱ', '教育', '旅游及景区',
        '酒店餐饮', '专业服务', '体育Ⅱ', '旅游零售Ⅱ', '互联网电商', '专业连锁Ⅱ', '一般零售', '贸易Ⅱ', '房地产服务',
        '房地产开发', '航运港口', '航空机场', '铁路公路', '物流', '燃气Ⅱ', '电力', '医疗服务', '医疗器械', '医药商业',
        '生物制品', '中药Ⅱ', '化学制药', '文娱用品', '家居用品', '包装印刷', '造纸', '饰品', '服装家纺', '纺织制造',
        '调味发酵品Ⅱ', '休闲食品', '饮料乳品', '非白酒', '白酒Ⅱ', '食品加工', '其他家电Ⅱ', '家电零部件Ⅱ', '照明设备Ⅱ',
        '厨卫电器', '小家电', '黑色家电', '白色家电', '商用车', '乘用车', '摩托车及其他', '汽车服务', '汽车零部件',
        '电子化学品Ⅱ', '消费电子', '其他电子Ⅱ', '光学光电子', '元件', '半导体', '能源金属', '小金属', '贵金属', '工业金属',
        '金属新材料', '特钢Ⅱ', '普钢', '冶钢原料', '非金属材料Ⅱ', '农化制品', '橡胶', '塑料', '化学纤维', '化学制品',
        '化学原料', '农业综合Ⅱ', '动物保健Ⅱ', '养殖业', '农产品加工', '饲料', '林业Ⅱ', '渔业', '种植业', '医疗美容',
        '化妆品', '个护用品', '环保设备Ⅱ', '环境治理', '炼化及贸易', '油服工程', '油气开采Ⅱ', '焦炭Ⅱ', '煤炭开采'
    ]
    class_stock = {}
    browser = webdriver.Chrome()
    url = 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000'
    browser.get(url)
    time.sleep(5)

    for class_name in class_names:
        try:
            time.sleep(1)
            ActionChains(browser).move_to_element(browser.find_element(by=By.XPATH, value='//*[@id="treeContainer"]/ul[1]/li[3]/a')).perform()
            browser.find_element(by=By.XPATH, value='//*[@id="treeContainer"]/ul[1]/li[3]/div/dl').find_element(by=By.LINK_TEXT, value=class_name).click()
            time.sleep(1)

            class_stock[class_name] = []

            if browser.find_element(by=By.XPATH, value='//*[@id="list_pages_top2"]').text == '':
                print('1')
                time.sleep(1)
                codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                for item in codes:
                    if len(item.text.split(' ')) > 2:
                        class_stock[class_name].append(item.text.split(' ')[:2])
            else:
                print('n')
                while True:
                    time.sleep(1)
                    codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                    for item in codes:
                        if len(item.text.split(' ')) > 2:
                            class_stock[class_name].append(item.text.split(' ')[:2])
                    next_page = browser.find_element(by=By.XPATH, value='/html/body/div[3]/div[5]/div[3]/div[3]/div/a[last()]')
                    if next_page.text == '下一页':
                        next_page.click()
                        continue
                    else:
                        break
        except:
            print(class_name, 'error')
            url = 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000'
            browser.get(url)
            time.sleep(5)
        else:
            print(class_name, 'finish', len(class_stock[class_name]))
    with open('申万二级类别.json', 'w') as sf:
        json.dump(class_stock, sf)


def get_class_3():
    class_names = [
        '其他数字媒体', '医美服务', '医美耗材', '品牌化妆品', '化妆品制造及其他', '洗护用品', '生活用纸', '环保设备Ⅲ',
        '综合环境治理', '固废治理', '水务及水治理', '大气治理', '其他石化', '油品石化贸易', '炼油化工', '油气及炼化工程',
        '油田服务', '油气开采Ⅲ', '焦炭Ⅲ', '焦煤', '动力煤', '其他通信设备', '通信终端及配件', '通信线缆及配套',
        '通信网络设备及器件', '通信应用增值服务', '通信工程及服务', '电信运营商', '电视广播Ⅲ', '大众出版', '教育出版',
        '文字媒体', '门户网站', '图片媒体', '视频媒体', '院线', '影视动漫制作', '广告媒体', '营销代理', '游戏Ⅲ',
        '横向通用软件', '垂直应用软件', 'IT服务Ⅲ', '其他计算机设备', '安防设备', '军工电子Ⅲ', '其他自动化设备', '激光设备',
        '工控设备', '机器人', '工程机械器件', '工程机械整机', '金属制品', '仪器仪表', '线缆部件及其他', '电工仪器仪表',
        '电网自动化设备', '配电设备', '输变电设备', '蓄电池及其他电池', '燃料电池', '锂电专用设备', '电池化学品', '锂电池',
        '风电零部件', '风电整机', '光伏加工设备', '光伏辅材', '逆变器', '光伏电池组件', '硅料硅片', '工程咨询服务Ⅲ',
        '园林工程', '基建市政工程', '涂料', '防水材料', '玻纤制造', '水泥制品', '其他多元金融', '资产管理', '金融信息服务',
        '租赁', '信托', '期货', '金融控股', '农商行Ⅲ', '城商行Ⅲ', '股份制银行Ⅲ', '国有大型银行Ⅲ', '教育运营及其他',
        '培训教育', '学历教育', '旅游综合', '自然景区', '人工景区', '餐饮', '酒店', '其他专业服务', '会展服务', '检测服务',
        '人力资源服务', '体育Ⅲ', '旅游零售Ⅲ', '电商服务', '跨境电商', '综合电商', '商业物业经营', '房产租赁经纪', '物业管理',
        '产业地产', '商业地产', '港口', '航运', '机场', '航空运输', '铁路运输', '公交', '高速公路', '公路货运', '仓储物流',
        '跨境物流', '快递', '中间产品及消费品供应链服务', '原材料供应链服务', '电能综合服务', '其他能源发电', '核力发电',
        '风力发电', '光伏发电', '其他医疗服务', '医院', '医疗研发外包', '诊断服务', '体外诊断', '医疗耗材', '医疗设备',
        '线下药店', '医药流通', '其他生物制品', '疫苗', '血液制品', '娱乐用品', '文化用品', '其他家居用品', '卫浴制品',
        '定制家居', '成品家居', '瓷砖地板', '综合包装', '纸包装', '塑料包装', '金属包装', '印刷', '特种纸', '大宗用纸',
        '其他饰品', '钟表珠宝', '非运动服装', '运动服装', '纺织鞋类制造', '调味发酵品Ⅲ', '熟食', '烘焙食品', '零食', '乳品',
        '软饮料', '其他酒类', '啤酒', '白酒Ⅲ', '保健品', '预加工食品', '其他家电Ⅲ', '家电零部件Ⅲ', '照明设备Ⅲ', '卫浴电器',
        '厨房电器', '个护小家电', '清洁小家电', '厨房小家电', '冰洗', '商用载客车', '商用载货车', '综合乘用车', '电动乘用车',
        '摩托车', '汽车综合服务', '汽车经销商', '汽车电子电气系统', '其他汽车零部件', '轮胎轮毂', '底盘与发动机系统',
        '车身附件及饰件', '电子化学品Ⅲ', '消费电子零部件及组装', '品牌消费电子', '半导体设备', '集成电路封测', '集成电路制造',
        '模拟芯片设计', '数字芯片设计', '锂', '钴', '钼', '白银', '特钢Ⅲ', '钢铁管材', '板材', '长材', '冶钢辅料', '铁矿石',
        '非金属材料Ⅲ', '复合肥', '钾肥', '农药', '磷肥及磷化工', '氮肥', '橡胶助剂', '膜材料', '合成树脂', '锦纶',
        '胶黏剂及胶带', '有机硅', '食品及饲料添加剂', '钛白粉', '煤化工', '农业综合Ⅲ', '其他养殖', '肉鸡养殖', '生猪养殖',
        '宠物食品', '水产饲料', '畜禽饲料', '食用菌', '航海装备Ⅲ', '地面兵装Ⅲ', '航空装备Ⅲ', '航天装备Ⅲ', '轨交设备Ⅲ',
        '其他专用设备', '印刷包装机械', '农用机械', '纺织服装设备', '楼宇设备', '能源及重型设备', '其他通用设备',
        '制冷空调设备', '磨具磨料', '机床工具', '其他电源设备Ⅲ', '火电设备', '综合电力设备商', '电机Ⅲ', '其他专业工程',
        '国际工程', '化学工程', '钢结构', '装修装饰Ⅲ', '房屋建设Ⅲ', '其他建材', '管材', '耐火材料', '玻璃制造', '水泥制造',
        '综合Ⅲ', '保险Ⅲ', '证券Ⅲ', '专业连锁Ⅲ', '多业态零售', '超市', '百货', '贸易Ⅲ', '住宅开发', '燃气Ⅲ', '热力服务',
        '水力发电', '火力发电', '中药Ⅲ', '化学制剂', '原料药', '家纺', '鞋帽及其他', '其他纺织', '辅料', '印染', '棉纺',
        '肉制品', '其他黑色家电', '彩电', '空调', '其他运输设备', '其他电子Ⅲ', '光学元件', 'LED', '面板', '被动元件',
        '印制电路板', '半导体材料', '分立器件', '其他小金属', '钨', '稀土', '黄金', '铅锌', '铜', '铝', '磁性材料',
        '其他金属新材料', '炭黑', '其他橡胶制品', '改性塑料', '其他塑料制品', '氨纶', '其他化学纤维', '粘胶', '涤纶', '聚氨酯',
        '氟化工', '其他化学制品', '纺织化学制品', '民爆制品', '涂料油墨', '其他化学原料', '无机盐', '氯碱', '纯碱',
        '动物保健Ⅲ', '其他农产品加工', '粮油加工', '果蔬加工', '林业Ⅲ', '水产养殖', '海洋捕捞', '其他种植业', '粮食种植',
        '种子'
    ]
    class_stock = {}
    browser = webdriver.Chrome()
    url = 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000'
    browser.get(url)
    time.sleep(5)

    for class_name in class_names:
        try:
            time.sleep(1)
            ActionChains(browser).move_to_element(browser.find_element(by=By.XPATH, value='//*[@id="treeContainer"]/ul[1]/li[4]/a')).perform()
            browser.find_element(by=By.XPATH, value='//*[@id="treeContainer"]/ul[1]/li[4]/div/dl').find_element(by=By.LINK_TEXT, value=class_name).click()
            time.sleep(1)

            class_stock[class_name] = []

            if browser.find_element(by=By.XPATH, value='//*[@id="list_pages_top2"]').text == '':
                print('1')
                time.sleep(1)
                codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                for item in codes:
                    if len(item.text.split(' ')) > 2:
                        class_stock[class_name].append(item.text.split(' ')[:2])
            else:
                print('n')
                while True:
                    time.sleep(1)
                    codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                    for item in codes:
                        if len(item.text.split(' ')) > 2:
                            class_stock[class_name].append(item.text.split(' ')[:2])
                    next_page = browser.find_element(by=By.XPATH, value='/html/body/div[3]/div[5]/div[3]/div[3]/div/a[last()]')
                    if next_page.text == '下一页':
                        next_page.click()
                        continue
                    else:
                        break
        except:
            print(class_name, 'error')
            url = 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000'
            browser.get(url)
            time.sleep(5)
        else:
            print(class_name, 'finish', len(class_stock[class_name]))
    with open('申万三级类别.json', 'w') as sf:
        json.dump(class_stock, sf)


def get_gainian():
    class_names = [
        '气凝胶', '土壤修复', '东数西算', '新冠药物', '幽门螺杆概念', '商汤科技概念', '冬奥会概念', '海洋经济', '手势识别',
        '虚拟数字人', '直流输电', 'DRG概念', 'EDR概念', '发电机概念', '绿色建筑', '空客概念', '培育钻石', '网约车概念',
        '华为欧拉', '绿色电力', '光热发电', '智慧矿山', '抽水蓄能', '元宇宙概念', 'NFT概念', '碳基材料', '北交所概念',
        '参股新三板', '环球影城', '碳化硅', '工业母机', '参股基金', '专精特新', '超宽带', '肝素', '态势感知', '逆变器',
        '职业教育', '应急管理', '电池管理', '退市警示', '超大盘', 'CRO概念', 'PVDF概念', '电池回收', '中欧班列', '绿色包装',
        '社区团购', '寒武纪概念', '爱奇艺概念', '呼吸机', '知识付费', '金刚线', '食药追溯', '电子化学品', '华为昇腾',
        '小鹏汽车概念', 'RISC概念', 'OBC概念', '植物照明', '空间站', '海水淡化', '口腔医疗', 'CDM概念', '砷化镓', '光电子',
        '湖北自贸区', '熔喷布', '防护服', '消毒概念', '消防概念', '长三角一体化', '钠电池', '数字能源', '植物蛋白', '华为鸿蒙',
        '预制菜', '盐湖提锂', '核废处理', '电子车牌', '葡萄酒', '微信概念', '烟标', '风沙治理', '生态园林', '百度概念',
        '特种气体', 'BIPV概念', '富时罗素概念', '折叠屏', '固态电池', '华为汽车', '茅概念', '城市大脑', '碳中和', '疫苗运输',
        '虚拟电厂', '有机硅', 'RCEP概念', '辅助生殖', '化妆品', '快手概念', '快充概念', '京东数科概念', '光刻机',
        '宁德时代概念', '第三代半导体', '汽车拆解', '换电概念', '代糖概念', '抖音小店', '中国电科集团', 'NMN概念', '海绵城市',
        '电子烟', '药用玻璃', '拼多多概念', 'GDR概念', '水产养殖', '食品检测', '盲盒概念', '字节跳动概念', '京东概念',
        '国六概念', '尾气处理', 'EDA概念', '免税概念', '送转填权', '生物安全', '头盔概念', '信创概念', 'REITs概念',
        '中芯国际概念', '农村电商', '卫星互联网', '油气存储', 'RCS概念', '原料药', 'C2M概念', '独角兽概念', 'IGBT概念',
        '网格化管理', 'IDC概念', '网络营销', '蔚来汽车概念', '存储器', '盖板玻璃', '磷酸铁锂', '氮化镓', 'WIFI概念',
        '医废处理', '在线办公', '体外诊断', '病毒检测', '口罩概念', '超级真菌', '可降解', '抗流感', '大基金概念', '特种玻璃',
        '铰链', 'LCP概念', '债转股', 'HIT电池', '转基因', '生物质能', '云视频', 'TOF概念', '传感器', 'MLED', '指纹识别',
        '云游戏', '光学', '油气管网', 'IPV6', '智能手表', '胎压监测', '无线耳机', '网红经济', '医疗美容', '船舶工业集团',
        '船舶重工集团', 'MLCC概念', '智能音箱', '腾讯云', '跨境电商', '风能', '智慧政务', '横琴新区', 'VPN概念', '全息概念',
        '智能交通', '数字货币', 'IP概念', '无线充电', '车联网', '智慧物流', '分拆概念', '可燃冰', '地理信息', '深圳国资',
        '西部开发', '智慧停车', '钴镍', '华为鲲鹏', '血液制品', '医药电商', '医用耗材', '眼科概念', '智慧医疗', '地下管廊',
        '冷链物流', '定制家居', '钛白粉', '民爆', '机器视觉', '智能穿戴', '无人机', '甲醇概念', '快递概念', '装配建筑',
        '轨道交通', '高校系', '维生素', '汽车电子', '光通信', '健康中国', '磷化工', '金融机具', '航母产业', '远洋运输',
        '氟化工', '激光概念', '壳资源', '垃圾分类', '青蒿素', '垃圾发电', '固废处理', '东北振兴', '农机', '零售药店',
        '养老产业', '国产乳业', '设计咨询', '整车', '黑龙江自贸区', '国资入股', '干细胞', '成渝城市群', 'ETC概念', '冰雪产业',
        '足球概念', '休闲食品', '大豆', '饲料', '园区开发', 'PCB概念', '光刻胶', '动物疫苗', '集成电路', '海底光缆',
        '操作系统', '华为海思', '数字乡村', '生物农药', '乡村振兴', '轮胎', '啤酒', '草甘膦', '养鸡', '种业', '人造肉概念',
        '价值成长', '透明工厂', '猪肉概念', '富士康概念', '央企金控', '券商相关', '流媒体', '纳米银线', '工业大麻', '铌概念',
        '网络切片', '供销社概念', '增持回购', '广东国资', '芬太尼概念', '麻醉概念', '美团概念', '谷歌概念', '进博会概念',
        '脸书概念', '中国化工集团', '深汕合作区', '中粮集团', '人脑工程', '钒电池', '雄安能化', '生态农业', '民营医院',
        '氢能源', '数字孪生', '电力物联网', '能源互联', '智能电网', '征信概念', '超高清', '信托概念', '互联金融', '3D打印',
        '金融科技', '柔性电子', '新基建', '边缘计算', '特高压', '土地流转', '油气改革', '高铁', '华为概念', '期货概念',
        '广电系', '旅游酒店', '中化集团', '短视频', '仿制药', '覆铜板', '金属铝', '全面屏', '山西国资', '融资租赁', '甘肃国资',
        '广西国资', '北京国资', '浙江国资', '福建国资', '江苏国资', '中核工业集团', '针状焦', '天津国资', '中科院系',
        '大唐集团', '中国建材集团', '新疆建设兵团', '航天科工集团', '航空工业集团', '航天科技集团', '复兴号', '国机集团',
        '特色小镇', '共享汽车', '家具卫浴', '禽流感药物', '锌电池', '特种钢', '多晶硅', 'GPU', '苹果产业链', '海南国资',
        '迪士尼', '深ST板', '国资改革', '青岛', '赛马概念', '小米概念', '6G概念', '腾讯概念', '工程机械', '汽车零部件',
        '网络直播', '无感支付', 'MSCI中国', '西藏国资', '数字经济', '贵州国资', 'ST板块', '知识产权', '工业互联网', '磁悬浮',
        '重工装备', '超级高铁', 'SAAS', '碳纤维', '兵工集团', '沥青概念', '兰州自贸区', '三元锂电', '杭州亚运', '国产软件',
        '航天航空', '智能电视', '湖南国资', '喀什规划区', '精准医疗', '嘉兴地区', '移动支付', '超级电容', '抗癌治癌',
        '单车概念', '纳米概念', '舟山自贸区', 'AMC概念', '农村电网', '平潭实验区', '环境监测', '水电', '福建自贸区',
        '电子发票', '在线旅游', '供应链金融', '电改', '石家庄', '汽车后市场', '汽车金融', '卫星导航', '清洁能源', '生物识别',
        '生态林业', '动力煤', '汽车轻量化', '液态金属', '价值品牌', '百货O2O', '互联网保险', '余热发电', '影视传媒', 'QLED',
        '沪警示板', '无锡国资委', '单晶硅', '生物医药', '引力波', '云印刷', '互联网家装', '细胞治疗', '电动物流车', '共享经济',
        '食品安全', '雄安环保', '雄安地产', '盐化工', '陶瓷概念', '雄安交运', '雄安基建', '雄安金融', '超导概念', '信息安全',
        '兵装集团', 'NFC概念', '安徽国资', '海南自贸区', '民用航空', '机械', '家用电器', '天然气', '自由贸易港', '新能源车',
        '芯片概念', '半导体', '新零售', '无人零售', '房屋租赁', '5G', '蚂蚁金服概念', '煤化工', '量子通信', '区块链', '新能源',
        '新材料', '新疆振兴', '虚拟现实', '雄安新区', '小盘', '小金属', '人脸识别', '人工智能', '上海国资', '融资融券', '手游',
        '水利建设', '水泥', '石墨烯', '燃料电池', '染料涂料', 'H股', '摘帽概念', '物联网', '铁路基建', '污水处理', '体育产业',
        '稀缺资源', '稀土永磁', '通用航空', '太阳能', '锂电池', '网络游戏', '网络安全', '特斯拉', '无人驾驶', 'LED',
        '央企改革', '粤港澳', '油气勘探', 'OLED', '在线教育', '云计算', '增强现实', '预盈预增', '影视动漫', '页岩气',
        '一带一路', '医疗器械', '疫苗', 'PM2.5', 'PPP概念', 'MCU概念', '苹果三星', '智能手机', '智能汽车', '智能机器',
        '智能家居', '智慧城市', '中石化系', '中药', '中盘', '中字头', '证金汇金', '阿里概念', '安防', '白酒', '北斗导航',
        '彩票', '充电桩', '军工电子', '次新股', '近端次新', '大数据', '大盘', '大飞机', '储能', '创投', '电子商务', '电子支付',
        '电子竞技', '多胎概念', '港口运输', '高送转', '股权转让', '工业4.0', '核电', '海工装备', '航天军工', '混改', '基因测序',
        '黄金股', '互联医疗', '沪自贸区', '节能环保', '举牌', '军民融合', '京津冀', '抗癌药物', '昨日涨停'
    ]

    class_stock = {}
    browser = webdriver.Chrome()
    url = 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000'
    browser.get(url)
    time.sleep(5)

    for class_name in class_names:
        try:
            time.sleep(1)
            ActionChains(browser).move_to_element(browser.find_element(by=By.XPATH, value='//*[@id="treeContainer"]/ul[1]/li[5]/a')).perform()
            browser.find_element(by=By.XPATH, value='//*[@id="treeContainer"]/ul[1]/li[5]/div/dl').find_element(by=By.LINK_TEXT, value=class_name).click()
            time.sleep(1)

            class_stock[class_name] = []

            if browser.find_element(by=By.XPATH, value='//*[@id="list_pages_top2"]').text == '':
                print('1')
                time.sleep(1)
                codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                for item in codes:
                    if len(item.text.split(' ')) > 2:
                        class_stock[class_name].append(item.text.split(' ')[:2])
            else:
                print('n')
                while True:
                    time.sleep(1)
                    codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                    for item in codes:
                        if len(item.text.split(' ')) > 2:
                            class_stock[class_name].append(item.text.split(' ')[:2])
                    next_page = browser.find_element(by=By.XPATH, value='/html/body/div[3]/div[5]/div[3]/div[3]/div/a[last()]')
                    if next_page.text == '下一页':
                        next_page.click()
                        continue
                    else:
                        break
        except:
            print(class_name, 'error')
            url = 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000'
            browser.get(url)
            time.sleep(5)
        else:
            print(class_name, 'finish', len(class_stock[class_name]))
    with open('热门概念.json', 'w') as sf:
        json.dump(class_stock, sf)


def get_bankuai():
    class_names = [
        '新疆维吾尔自治区', '宁夏回族自治区', '青海省', '甘肃省', '陕西省', '西藏自治区', '云南省', '贵州省', '四川省',
        '重庆市', '海南省', '广西壮族自治区', '广东省', '湖南省', '湖北省', '河南省', '山东省', '江西省', '福建省', '安徽省',
        '浙江省', '江苏省', '上海市', '黑龙江省', '吉林省', '辽宁省', '内蒙古自治区', '山西省', '河北省', '天津市', '北京市'
    ]
    class_stock = {}

    browser = webdriver.chrome.webdriver.WebDriver(executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')
    url = 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000'
    browser.get(url)
    time.sleep(5)

    for class_name in class_names:
        try:
            time.sleep(5)
            ActionChains(browser).move_to_element(browser.find_element(by=By.XPATH, value='//*[@id="treeContainer"]/ul[1]/li[6]/a')).perform()
            browser.find_element(by=By.XPATH, value='//*[@id="treeContainer"]/ul[1]/li[6]/div/dl').find_element(by=By.LINK_TEXT, value=class_name).click()
            time.sleep(1)

            class_stock[class_name] = []

            if browser.find_element(by=By.XPATH, value='//*[@id="list_pages_top2"]').text == '':
                print('1')
                time.sleep(1)
                codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                for item in codes:
                    if len(item.text.split(' ')) > 2:
                        class_stock[class_name].append(item.text.split(' ')[:2])
            else:
                print('n')
                while True:
                    time.sleep(1)
                    codes = browser.find_elements(by=By.XPATH, value='//*[@id="tbl_wrap"]/table/tbody/tr')
                    for item in codes:
                        if len(item.text.split(' ')) > 2:
                            class_stock[class_name].append(item.text.split(' ')[:2])
                    next_page = browser.find_element(by=By.XPATH, value='/html/body/div[3]/div[5]/div[3]/div[3]/div/a[last()]')
                    if next_page.text == '下一页':
                        next_page.click()
                        continue
                    else:
                        break
        except:
            print(class_name, 'error')
            url = 'https://vip.stock.finance.sina.com.cn/mkt/#sw1_740000'
            browser.get(url)
            time.sleep(5)
        else:
            print(class_name, 'finish', len(class_stock[class_name]))
    with open('地域板块.json', 'w') as sf:
        json.dump(class_stock, sf)


if __name__ == '__main__':
    print(31+131+335+562+31)
