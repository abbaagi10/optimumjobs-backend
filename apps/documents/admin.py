from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'document_type', 'owner', 'file_size', 'uploaded_at']
    list_filter = ['document_type']
    search_fields = ['owner__email', 'original_filename']
    readonly_fields = ['file_size', 'mime_type', 'uploaded_at']