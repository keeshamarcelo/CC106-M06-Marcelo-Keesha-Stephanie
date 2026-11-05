
from django.shortcuts import render

def landing(request):
    return render(request, 'home/landing.html')

def home(request):
    context = {
        'title': 'My Home Page',
        'show_message': True,
        'message': 'Welcome to my first Django application!',
    }
    return render(request, 'home/home.html', context)