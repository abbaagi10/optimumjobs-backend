from rest_framework import permissions

from apps.organizations.models import OrganizationMember


class IsOpportunityOrgMember(permissions.BasePermission):
    """
    Autorise l'accès en écriture uniquement si l'utilisateur est membre
    (n'importe quel rôle) de l'organisation propriétaire de l'opportunité.
    """

    def has_object_permission(self, request, view, obj):
        return OrganizationMember.objects.filter(
            organization=obj.organization, user=request.user
        ).exists()