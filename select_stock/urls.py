from django.urls import path
from . import views


urlpatterns = [
    # path('', views.stock_list, name='stock_list'),
    path('add_select_stock/', views.add_select_stock, name='add_select_stock'),
    path('get_select_stock/', views.get_select_stock, name='get_select_stock'),
    # path('type/<str:type_name>/<int:stock_type_id>', views.stock_type, name='stock_type'),
]
