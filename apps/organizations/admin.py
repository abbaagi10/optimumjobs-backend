from django.contrib import admin

from .models import Organization, OrganizationMember


class OrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'is_verified', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['name']
    inlines = [OrganizationMemberInline]