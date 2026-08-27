from django.urls import path

from .views import (
    MyProfileView,
    ExperienceListCreateView, ExperienceDetailView,
    EducationListCreateView, EducationDetailView,
    LanguageListCreateView, LanguageDetailView,
)

urlpatterns = [
    path('profile/', MyProfileView.as_view(), name='my-profile'),

    path('profile/experiences/', ExperienceListCreateView.as_view(), name='experience-list'),
    path('profile/experiences/<int:pk>/', ExperienceDetailView.as_view(), name='experience-detail'),

    path('profile/education/', EducationListCreateView.as_view(), name='education-list'),
    path('profile/education/<int:pk>/', EducationDetailView.as_view(), name='education-detail'),

    path('profile/languages/', LanguageListCreateView.as_view(), name='language-list'),
    path('profile/languages/<int:pk>/', LanguageDetailView.as_view(), name='language-detail'),
]