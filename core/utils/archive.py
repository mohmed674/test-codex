import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def archive_file(file_obj, folder='general'):
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'archives', folder))
    filename = fs.save(file_obj.name, file_obj)
    return fs.url(filename)
