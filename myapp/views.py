from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.
def index(request): # Исправил опечатку: reqest на request
    return render(request, 'myapp/index.html')
def about(request): # Исправил опечатку: reqest на request
    return render(request, 'myapp/about.html')
def contact(request): # Исправил опечатку: reqest на request
    return render(request, 'myapp/contact.html')