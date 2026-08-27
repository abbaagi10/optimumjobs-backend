from django.contrib import admin

from .models import Opportunity, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'opportunity_type', 'status', 'created_at']
    list_filter = ['status', 'opportunity_type', 'is_remote']
    search_fields = ['title', 'organization__name']
    readonly_fields = ['created_at', 'updated_at', 'published_at']