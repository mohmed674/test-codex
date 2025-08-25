from django.shortcuts import render

def index(request):
    return render(request, 'audit_out/index.html')


def app_home(request):
    return render(request, 'apps/audit_out/home.html', {'app': 'audit_out'})
