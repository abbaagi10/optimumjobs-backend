from django.contrib import admin

from .models import Application, ApplicationDocument


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'opportunity', 'status', 'submitted_at']
    list_filter = ['status']
    search_fields = ['candidate__user__email', 'opportunity__title']
    inlines = [ApplicationDocumentInline]