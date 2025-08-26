from django.contrib import admin

from .models import Folder, Tag, MediaFile


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "created_at")
    search_fields = ("name",)
    list_filter = ("parent",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "folder", "uploaded_at", "is_active")
    search_fields = ("name", "description", "file")
    list_filter = ("folder", "tags", "is_active")
