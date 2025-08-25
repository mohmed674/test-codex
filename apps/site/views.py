from django.shortcuts import render

def home(request):
    return render(request, 'site/home.html')

def about(request):
    return render(request, 'site/about.html')

def contact(request):
    return render(request, 'site/contact.html')


def app_home(request):
    return render(request, 'apps/site/home.html', {'app': 'site'})
