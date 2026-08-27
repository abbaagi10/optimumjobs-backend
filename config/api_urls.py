from django.urls import path, include

urlpatterns = [
    # Les routes des apps (users, opportunities, etc.) seront ajoutées ici
    path('', include('apps.users.urls')),
]