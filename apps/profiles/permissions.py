from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """
    Autorise l'accès à un sous-objet du profil (Experience, Education, Language)
    uniquement si ce sous-objet appartient au profil du candidat connecté.
    """

    def has_object_permission(self, request, view, obj):
        return obj.profile.user == request.user