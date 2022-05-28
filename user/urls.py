from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_and_register, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user_info/', views.user_info, name='user_info'),
]