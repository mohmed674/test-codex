from django.shortcuts import render

def index(request):
    return render(request, 'templates/index.html')


def app_home(request):
    return render(request, 'apps/templates/home.html', {'app': 'templates'})
