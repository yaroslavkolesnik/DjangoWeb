# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Вход (используем готовую 'смотрелку' Django)
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),

    # Выход (тоже готовая)
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

    # Регистрация (напишем сами в views.py)
    path('register/', views.register, name='register'),
]