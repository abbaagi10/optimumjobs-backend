from rest_framework import permissions

from .models import OrganizationMember


class IsOrganizationMember(permissions.BasePermission):
    """
    Autorise l'accès uniquement si l'utilisateur connecté est membre
    de l'organisation ciblée par l'objet (obj.organization ou obj lui-même
    s'il s'agit directement d'une Organization).
    """

    def has_object_permission(self, request, view, obj):
        organization = obj if hasattr(obj, 'members') else getattr(obj, 'organization', None)
        if organization is None:
            return False
        return OrganizationMember.objects.filter(
            organization=organization, user=request.user
        ).exists()


class IsOrganizationManager(permissions.BasePermission):
    """
    Autorise l'accès uniquement si l'utilisateur connecté est OWNER ou MANAGER
    de l'organisation ciblée. Utilisé pour les actions sensibles
    (gérer les membres, modifier les paramètres de l'organisation).
    """

    def has_object_permission(self, request, view, obj):
        organization = obj if hasattr(obj, 'members') else getattr(obj, 'organization', None)
        if organization is None:
            return False
        return OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            role__in=[OrganizationMember.Role.OWNER, OrganizationMember.Role.MANAGER],
        ).exists()