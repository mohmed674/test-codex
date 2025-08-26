from django.views.generic import DetailView, ListView

from .models import MediaFile, Folder


class MediaFileListView(ListView):
    model = MediaFile
    paginate_by = 20


class MediaFileDetailView(DetailView):
    model = MediaFile


class FolderListView(ListView):
    model = Folder
    paginate_by = 20
