"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.conf.urls.i18n import i18n_patterns

# Маршруты, которые будут иметь префикс языка
urlpatterns = i18n_patterns(
    path("", views.index, name='home'),
    path("about/", views.about, name='about'),
    path("contact/", views.contact, name='contact'),
    path("show/", views.show, name='show'),
    path("favorites/", views.favorites, name='favorites'),
    path("order/", views.order, name='order'),
    path('admin/', admin.site.urls),
)

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
]

handler400 = 'myapp.views.handler400'
handler404 = 'myapp.views.handler404'
handler405 = 'myapp.views.handler405'
handler500 = 'myapp.views.handler500'