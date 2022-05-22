import os
from django.db.models import Q
from stock.models import Stock
from django.shortcuts import render


# Create your views here.
def search(request):
    search_word = request.GET.get('search-word')
    search_stocks = Stock.objects.filter(
        Q(stock_code__icontains=search_word) |
        Q(stock_name__icontains=search_word) |
        Q(stock_company__icontains=search_word) |
        Q(stock_place__icontains=search_word) |
        Q(shenwan_1__icontains=search_word) |
        Q(shenwan_2__icontains=search_word) |
        Q(shenwan_3__icontains=search_word)
    )

    res_dist = {
        'search_word': search_word,
        'search_stocks': search_stocks.distinct()
    }
    return render(request, 'search/search_list.html', res_dist)

