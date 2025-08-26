from django.urls import path

from .views import MediaFileListView, MediaFileDetailView, FolderListView

urlpatterns = [
    path("", MediaFileListView.as_view(), name="media_index"),
    path("files/<int:pk>/", MediaFileDetailView.as_view(), name="media_detail"),
    path("folders/", FolderListView.as_view(), name="media_folders"),
]
