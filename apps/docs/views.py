from django.shortcuts import render

def index(request):
    return render(request, 'docs/index.html')


def app_home(request):
    return render(request, 'apps/docs/home.html', {'app': 'docs'})
