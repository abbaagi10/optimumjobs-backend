from rest_framework import permissions
from apps.organizations.models import OrganizationMember


class IsOpportunityOrgMember(permissions.BasePermission):
    """
    Autorise l'accès en écriture si :
    - L'utilisateur est membre de l'organisation propriétaire
    - OU l'utilisateur est un administrateur
    """

    def has_object_permission(self, request, view, obj):
        # ✅ Les administrateurs ont tous les droits
        if request.user and request.user.role == 'admin':
            return True
        
        # ✅ Vérifier si l'utilisateur est membre de l'organisation
        return OrganizationMember.objects.filter(
            organization=obj.organization, 
            user=request.user
        ).exists()