from django.urls import path, include

urlpatterns = [
    # Les routes des apps (users, opportunities, etc.) seront ajoutées ici
    path('', include('apps.users.urls')),
    path('', include('apps.profiles.urls')),
    path('', include('apps.organizations.urls')),
    path('', include('apps.opportunities.urls')),
    path('', include('apps.applications.urls')),
     path('', include('apps.documents.urls')),
]