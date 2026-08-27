from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError

from apps.core.permissions import IsOrganization
from .models import Organization, OrganizationMember
from .permissions import IsOrganizationMember, IsOrganizationManager
from .serializers import OrganizationSerializer, OrganizationMemberSerializer


class OrganizationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/organizations/   -> lister les organisations dont je suis membre
    POST /api/v1/organizations/   -> créer une organisation (je deviens automatiquement OWNER)
    """
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganization]

    def get_queryset(self):
        return Organization.objects.filter(members__user=self.request.user)

    def perform_create(self, serializer):
        organization = serializer.save()
        OrganizationMember.objects.create(
            organization=organization,
            user=self.request.user,
            role=OrganizationMember.Role.OWNER,
        )


class OrganizationDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/organizations/{id}/   -> voir le détail (si membre)
    PATCH /api/v1/organizations/{id}/   -> modifier (si OWNER/MANAGER uniquement)
    """
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), IsOrganizationMember()]
        return [permissions.IsAuthenticated(), IsOrganizationManager()]


class OrganizationMemberListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/organizations/{org_id}/members/   -> lister les membres (si membre)
    POST /api/v1/organizations/{org_id}/members/   -> ajouter un membre (si OWNER/MANAGER)
    """
    serializer_class = OrganizationMemberSerializer

    def get_organization(self):
        return Organization.objects.get(pk=self.kwargs['org_id'])

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), IsOrganizationMember()]
        return [permissions.IsAuthenticated(), IsOrganizationManager()]

    def check_permissions(self, request):
        super().check_permissions(request)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        organization = self.get_organization()
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, organization):
                self.permission_denied(request, message="Vous n'êtes pas autorisé à effectuer cette action.")

    def get_queryset(self):
        return OrganizationMember.objects.filter(organization_id=self.kwargs['org_id'])

    def perform_create(self, serializer):
        organization = self.get_organization()
        serializer.save(organization=organization)