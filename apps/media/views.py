from django.views.generic import DetailView, ListView
from .models import MediaFile, Folder


class MediaFileListView(ListView):
    model = MediaFile
    template_name = 'media/mediafile_list.html'
    context_object_name = 'files'


class MediaFileDetailView(DetailView):
    model = MediaFile
    template_name = 'media/mediafile_detail.html'
    context_object_name = 'file'


class FolderListView(ListView):
    model = Folder
    template_name = 'media/folder_list.html'
    context_object_name = 'folders'
