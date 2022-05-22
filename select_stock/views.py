import os
import json
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from django.http import JsonResponse
from .models import SelectStock
from stock.models import Stock


def get_page_num(page_num, stocks_all_list):
    paginator = Paginator(stocks_all_list, 10)
    page_of_stocks = paginator.get_page(page_num)
    current_page_num = page_of_stocks.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + list(
        range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    return page_of_stocks, page_range


def get_stocks_price(stocks):
    with open(settings.PRICE_ROOT + '/stock_dict.json', 'r', encoding='utf-8') as rf:
        stock_dict = json.load(rf)
    stock_price = []
    for stock in stocks.object_list:
        if stock.stock_code in stock_dict:
            stock_data = stock_dict[stock.stock_code]
            stock_price.append({
                'stock': stock,
                'last_price': round(stock_data['last_price'], 4),  # 最新价格
                'diff_price': round(stock_data['diff_price'], 4),  # 涨跌额
                'diff_ratio': str(round(stock_data['diff_ratio'], 2)) + '%',  # 涨跌幅
                'max_price': round(stock_data['max_price'], 4),  # 最高
                'min_price': round(stock_data['min_price'], 4),  # 最低
                'sign': 'red' if stock_data['diff_price'] > 0 else 'green' if stock_data['diff_price'] < 0 else 'grey',
            })
    return stock_price


def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)


def SuccessResponse(message):
    data = {}
    data['status'] = 'SUCCESS'
    data['message'] = message
    return JsonResponse(data)


def add_select_stock(request):
    user = request.user
    if not user.is_authenticated:
        return ErrorResponse(400, 'you were not login')
    stock_id = request.GET.get('stock_id')
    print(stock_id)
    try:
        stock_obj = Stock.objects.get(pk=stock_id)
        selected, created = SelectStock.objects.get_or_create(user=user, stock=stock_obj)
        return SuccessResponse('add select stock finished!')
    except:
        return ErrorResponse(402, 'stock not found!')


def get_select_stock(request):
    user = request.user
    if not user.is_authenticated:
        return ErrorResponse(400, 'you were not login')
    select_stock_list = [i.stock for i in SelectStock.objects.filter(user=user)]

    # 页码
    page_num = request.GET.get('page', 1)
    page_of_stocks, page_range = get_page_num(page_num, select_stock_list)

    # 价格
    stock_price = get_stocks_price(page_of_stocks)

    res_dist = {
        'stocks': stock_price,
        'page_of_stocks': page_of_stocks,
        'page_range': page_range
    }
    return render(request, 'select_stock/select_stock.html', res_dist)


