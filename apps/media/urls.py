from django.urls import path
from .views import (
    MediaFileListView,
    MediaFileDetailView,
    FolderListView,
)

app_name = 'media'

urlpatterns = [
    path('', MediaFileListView.as_view(), name='file_list'),
    path('files/<int:pk>/', MediaFileDetailView.as_view(), name='file_detail'),
    path('folders/', FolderListView.as_view(), name='folder_list'),
]
