from rest_framework import permissions

from apps.organizations.models import OrganizationMember


class IsApplicationOwner(permissions.BasePermission):
    """
    Autorise uniquement le candidat propriétaire de la candidature.
    """

    def has_object_permission(self, request, view, obj):
        return obj.candidate.user == request.user


class IsApplicationOrgMember(permissions.BasePermission):
    """
    Autorise uniquement un membre de l'organisation propriétaire de l'opportunité
    concernée par cette candidature.
    """

    def has_object_permission(self, request, view, obj):
        return OrganizationMember.objects.filter(
            organization=obj.opportunity.organization, user=request.user
        ).exists()