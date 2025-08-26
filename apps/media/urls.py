from django.http import HttpResponse
from django.urls import path


def index(request):
    return HttpResponse("media index")


urlpatterns = [
    path('', index, name='media-index'),
]
