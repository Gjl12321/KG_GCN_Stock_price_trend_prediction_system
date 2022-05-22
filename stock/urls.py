from django.urls import path
from . import views


urlpatterns = [
    # path('', views.stock_list, name='stock_list'),
    path('<str:show_list>', views.stock_list, name='stock_list'),
    path('stock_detail/<int:stock_id>', views.stock_detail, name='stock_detail'),
]
