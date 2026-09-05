# apps/profiles/urls.py
# C:\optimumjobs-backend\apps\profiles\urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Mon profil (authentifié)
    path('profile/', views.MyProfileView.as_view(), name='my-profile'),
    
    # Profil public d'un candidat (pour les organisations)
    path('profile/<int:pk>/', views.PublicProfileView.as_view(), name='public-profile'),
    
    # Expériences
    path('profile/experiences/', views.ExperienceListCreateView.as_view(), name='experience-list'),
    path('profile/experiences/<int:pk>/', views.ExperienceDetailView.as_view(), name='experience-detail'),
    
    # Formations
    path('profile/education/', views.EducationListCreateView.as_view(), name='education-list'),
    path('profile/education/<int:pk>/', views.EducationDetailView.as_view(), name='education-detail'),
    
    # Langues
    path('profile/languages/', views.LanguageListCreateView.as_view(), name='language-list'),
    path('profile/languages/<int:pk>/', views.LanguageDetailView.as_view(), name='language-detail'),
]