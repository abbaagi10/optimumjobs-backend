from django.contrib import admin

from .models import CandidateProfile, Experience, Education, Language


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'city', 'country']
    search_fields = ['user__email', 'first_name', 'last_name']
    inlines = [ExperienceInline, EducationInline, LanguageInline]