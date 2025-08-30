from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
# Create your views here.
def index(request):
    return render(request, 'myapp/index.html')
def about(request):
    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': _('О нас'), 'url': reverse('about')},
    ]
    context = {'breadcrumbs': breadcrumbs}
    return render(request, 'myapp/about.html', context)
def contact(request):
    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': _('Контакты'), 'url': reverse('contact')},
    ]
    context = {'breadcrumbs': breadcrumbs}
    return render(request, 'myapp/contact.html', context)

def show(request):
    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': _('Товар'), 'url': reverse('show')},
    ]
    context = {'breadcrumbs': breadcrumbs}
    return render(request, 'myapp/show.html', context)
def favorites(request):
    return render(request, 'myapp/favorites.html')

def order(request):
    return render(request, 'myapp/order.html')


def handler404(request, exception):
    return render(request, 'myapp/404.html', status=404)

def handler400(request, exception):

    return render(request, 'myapp/400.html', status=400)

def handler405(request, exception):

    return render(request, 'myapp/405.html', status=405)

def handler500(request):

    return render(request, 'myapp/500.html', status=500)