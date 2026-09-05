# apps/opportunities/views.py
# VERSION COMPLÈTE CORRIGÉE

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsOrganization
from apps.organizations.models import OrganizationMember
from .models import Opportunity
from .permissions import IsOpportunityOrgMember
from .serializers import OpportunityPublicSerializer, OpportunityManageSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

from rest_framework import filters as drf_filters
from .filters import OpportunityFilter


class PublicOpportunityListView(generics.ListAPIView):
    """
    GET /api/v1/opportunities/
    Filtres exacts : ?type=job&city=Niamey&is_remote=true&category=1&skills=1,3
    Recherche : ?search=django
    Tri : ?ordering=-created_at  ou  ?ordering=salary_min
    """
    # ✅ CHANGER : Ne pas filtrer par défaut
    queryset = Opportunity.objects.all()
    permission_classes = [permissions.AllowAny]

    filterset_class = OpportunityFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'published_at', 'salary_min', 'application_deadline']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        ✅ Utiliser le bon serializer selon le rôle de l'utilisateur
        """
        user = self.request.user
        # Si l'utilisateur est admin, utiliser le serializer complet
        if user and user.is_authenticated and user.role == 'admin':
            return OpportunityManageSerializer
        # Sinon, utiliser le serializer public
        return OpportunityPublicSerializer

    def get_queryset(self):
        """
        ✅ Filtrer selon le rôle de l'utilisateur et les paramètres
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 🔥 Si l'utilisateur est admin, retourner toutes les offres (avec filtres)
        if user and user.is_authenticated and user.role == 'admin':
            # Appliquer le filtre de statut si présent
            status_param = self.request.query_params.get('status')
            if status_param:
                queryset = queryset.filter(status=status_param)
            return queryset
        
        # 🔥 Si l'utilisateur est une organisation, montrer ses offres + publiées
        if user and user.is_authenticated and user.role == 'organization':
            # Montrer les offres publiées + les offres de l'organisation
            org_ids = OrganizationMember.objects.filter(user=user).values_list('organization_id', flat=True)
            queryset = queryset.filter(
                models.Q(status=Opportunity.Status.PUBLISHED) |
                models.Q(organization_id__in=org_ids)
            )
            return queryset
        
        # 🔥 Pour les utilisateurs non authentifiés ou candidats
        # Ne montrer que les offres PUBLISHED
        return queryset.filter(status=Opportunity.Status.PUBLISHED)


class PublicOpportunityDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/opportunities/{id}/  -> détail public (uniquement si publiée)
    """
    queryset = Opportunity.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        user = self.request.user
        if user and user.is_authenticated and user.role == 'admin':
            return OpportunityManageSerializer
        return OpportunityPublicSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin peut voir toutes les offres
        if user and user.is_authenticated and user.role == 'admin':
            return queryset
        
        # Sinon, seulement PUBLISHED
        return queryset.filter(status=Opportunity.Status.PUBLISHED)


class MyOrganizationOpportunityListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/organizations/{org_id}/opportunities/  -> opportunités de mon organisation (tous statuts)
    POST /api/v1/organizations/{org_id}/opportunities/  -> créer une opportunité (statut initial DRAFT)
    """
    serializer_class = OpportunityManageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganization]

    def get_queryset(self):
        return Opportunity.objects.filter(
            organization_id=self.kwargs['org_id'],
            organization__members__user=self.request.user,
        )

    def perform_create(self, serializer):
        is_member = OrganizationMember.objects.filter(
            organization_id=self.kwargs['org_id'], user=self.request.user
        ).exists()
        if not is_member:
            raise PermissionDenied("Vous n'êtes pas membre de cette organisation.")
        serializer.save(organization_id=self.kwargs['org_id'], status=Opportunity.Status.DRAFT)


class MyOrganizationOpportunityDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/opportunities/manage/{id}/  -> détail complet (si membre de l'organisation)
    PATCH /api/v1/opportunities/manage/{id}/  -> modifier (uniquement si DRAFT ou REJECTED)
    """
    serializer_class = OpportunityManageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganization, IsOpportunityOrgMember]
    queryset = Opportunity.objects.all()

    def perform_update(self, serializer):
        opportunity = self.get_object()
        if opportunity.status not in [Opportunity.Status.DRAFT, Opportunity.Status.REJECTED]:
            raise ValidationError(
                "Une opportunité ne peut être modifiée que si elle est en brouillon ou rejetée."
            )
        serializer.save()


class SubmitForReviewView(APIView):
    """
    POST /api/v1/opportunities/manage/{id}/submit/
    Transition : DRAFT -> PENDING_REVIEW
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganization, IsOpportunityOrgMember]

    @extend_schema(
        summary="Soumettre une opportunité pour validation",
        description="Fait passer une opportunité de DRAFT (ou REJECTED) à PENDING_REVIEW.",
        request=None,
        responses={200: OpportunityManageSerializer, 400: OpenApiResponse(description="Transition invalide")},
    )

    def post(self, request, pk):
        opportunity = generics.get_object_or_404(Opportunity, pk=pk)
        self.check_object_permissions(request, opportunity)

        if opportunity.status not in [Opportunity.Status.DRAFT, Opportunity.Status.REJECTED]:
            return Response(
                {"detail": "Seule une opportunité en brouillon ou rejetée peut être soumise."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        opportunity.status = Opportunity.Status.PENDING_REVIEW
        opportunity.rejection_reason = ''
        opportunity.save()
        return Response(OpportunityManageSerializer(opportunity).data)


class ReviewOpportunityView(APIView):
    """
    POST /api/v1/opportunities/manage/{id}/review/
    Réservé à l'administrateur. Transition : PENDING_REVIEW -> APPROVED ou REJECTED
    Body attendu : {"action": "approve"} ou {"action": "reject", "reason": "..."}
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        opportunity = generics.get_object_or_404(Opportunity, pk=pk)

        if opportunity.status != Opportunity.Status.PENDING_REVIEW:
            return Response(
                {"detail": "Seule une opportunité en attente de validation peut être examinée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = request.data.get('action')
        if action == 'approve':
            opportunity.status = Opportunity.Status.APPROVED
        elif action == 'reject':
            opportunity.status = Opportunity.Status.REJECTED
            opportunity.rejection_reason = request.data.get('reason', '')
        else:
            return Response({"detail": "action doit être 'approve' ou 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        opportunity.save()
        return Response(OpportunityManageSerializer(opportunity).data)


class PublishOpportunityView(APIView):
    """
    POST /api/v1/opportunities/manage/{id}/publish/
    Transition : APPROVED -> PUBLISHED
    Peut être déclenché par l'organisation (une fois approuvée) ou l'admin.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        opportunity = generics.get_object_or_404(Opportunity, pk=pk)

        is_org_member = OrganizationMember.objects.filter(
            organization=opportunity.organization, user=request.user
        ).exists()
        is_admin = request.user.role == 'admin' or request.user.is_staff
        if not (is_org_member or is_admin):
            raise PermissionDenied()

        if opportunity.status != Opportunity.Status.APPROVED:
            return Response(
                {"detail": "Seule une opportunité approuvée peut être publiée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        opportunity.status = Opportunity.Status.PUBLISHED
        opportunity.published_at = timezone.now()
        opportunity.save()
        return Response(OpportunityManageSerializer(opportunity).data)


class CloseOpportunityView(APIView):
    """
    POST /api/v1/opportunities/manage/{id}/close/
    Transition : PUBLISHED -> CLOSED
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganization, IsOpportunityOrgMember]

    def post(self, request, pk):
        opportunity = generics.get_object_or_404(Opportunity, pk=pk)
        self.check_object_permissions(request, opportunity)

        if opportunity.status != Opportunity.Status.PUBLISHED:
            return Response(
                {"detail": "Seule une opportunité publiée peut être clôturée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        opportunity.status = Opportunity.Status.CLOSED
        opportunity.save()
        return Response(OpportunityManageSerializer(opportunity).data)