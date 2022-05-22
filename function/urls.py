from django.urls import path
from . import views


urlpatterns = [
    path('daily/', views.news_list, name='news_list'),
    path('daily/<str:news_type>', views.news_daily, name='news_daily'),
    path('knowledge_graph/', views.knowledge_graph, name='knowledge_graph'),
    path('predict/', views.predict, name='predict'),
]
