from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from .forms import LoginForm, RegForm


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))


# def user_info(request):
#     context = {}
#     return render(request, 'user/user_info.html', context)


def login_and_register(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))

        reg_form = RegForm(request.POST)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()
        reg_form = RegForm()

    context = {
        'login_form': login_form,
        'reg_form': reg_form
    }
    return render(request, 'user/login-register.html', context)


