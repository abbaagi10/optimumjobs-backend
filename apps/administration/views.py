from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.users.serializers import UserSerializer
from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationSerializer
from apps.opportunities.models import Opportunity
from apps.opportunities.serializers import OpportunityManageSerializer
from apps.applications.models import Application

from django.contrib.auth import get_user_model

User = get_user_model()


class AdminUserListView(generics.ListAPIView):
    """
    GET /api/v1/admin/users/
    GET /api/v1/admin/users/?role=candidate
    GET /api/v1/admin/users/?is_active=false
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        return queryset


class AdminToggleUserActiveView(APIView):
    """
    POST /api/v1/admin/users/{id}/toggle-active/
    Active ou désactive un compte utilisateur.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        user = generics.get_object_or_404(User, pk=pk)

        if user.is_superuser:
            return Response(
                {"detail": "Impossible de désactiver un superutilisateur via cet endpoint."},
                status=400,
            )

        user.is_active = not user.is_active
        user.save()
        return Response(UserSerializer(user).data)


class AdminOrganizationListView(generics.ListAPIView):
    """
    GET /api/v1/admin/organizations/
    GET /api/v1/admin/organizations/?is_verified=false
    """
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Organization.objects.all().order_by('-created_at')
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=(is_verified.lower() == 'true'))
        return queryset


class AdminVerifyOrganizationView(APIView):
    """
    POST /api/v1/admin/organizations/{id}/verify/
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        organization = generics.get_object_or_404(Organization, pk=pk)
        organization.is_verified = True
        organization.save()
        return Response(OrganizationSerializer(organization, context={'request': request}).data)


class AdminPendingOpportunityListView(generics.ListAPIView):
    """
    GET /api/v1/admin/opportunities/pending/
    Liste les opportunités en attente de validation - vue pratique pour le dashboard,
    évite à l'admin de deviner l'ID d'une opportunité à valider.
    """
    serializer_class = OpportunityManageSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Opportunity.objects.filter(status=Opportunity.Status.PENDING_REVIEW)


class AdminDashboardStatsView(APIView):
    """
    GET /api/v1/admin/dashboard/
    Statistiques globales pour la page d'accueil du dashboard admin.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({
            "users": {
                "total": User.objects.count(),
                "candidates": User.objects.filter(role='candidate').count(),
                "organizations": User.objects.filter(role='organization').count(),
                "inactive": User.objects.filter(is_active=False).count(),
            },
            "organizations": {
                "total": Organization.objects.count(),
                "verified": Organization.objects.filter(is_verified=True).count(),
                "unverified": Organization.objects.filter(is_verified=False).count(),
            },
            "opportunities": {
                "total": Opportunity.objects.count(),
                "pending_review": Opportunity.objects.filter(status=Opportunity.Status.PENDING_REVIEW).count(),
                "published": Opportunity.objects.filter(status=Opportunity.Status.PUBLISHED).count(),
            },
            "applications": {
                "total": Application.objects.count(),
                "submitted": Application.objects.filter(status=Application.Status.SUBMITTED).count(),
            },
        })