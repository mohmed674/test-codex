from django.shortcuts import render

def index(request):
    return render(request, 'themes/index.html')


def app_home(request):
    return render(request, 'apps/themes/home.html', {'app': 'themes'})
