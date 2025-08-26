from django.contrib import admin
from .models import Folder, Tag, MediaFile


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'updated_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'folder', 'size', 'content_type', 'uploaded_at', 'is_active'
    )
    search_fields = ('name', 'description', 'content_type')
    list_filter = (
        'uploaded_at', 'is_active', 'content_type', 'folder'
    )
