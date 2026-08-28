from django.db import IntegrityError, transaction
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsCandidate
from apps.opportunities.models import Opportunity
from apps.profiles.models import CandidateProfile
from apps.organizations.models import OrganizationMember
from .models import Application
from .permissions import IsApplicationOwner, IsApplicationOrgMember
from .serializers import ApplicationSerializer, ApplicationCreateSerializer, ApplicationStatusUpdateSerializer


class ApplyToOpportunityView(APIView):
    """
    POST /api/v1/opportunities/{id}/apply/
    Le candidat postule à une opportunité publiée.
    """
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def post(self, request, pk):
        opportunity = generics.get_object_or_404(Opportunity, pk=pk)
        profile, _ = CandidateProfile.objects.get_or_create(user=request.user)

        serializer = ApplicationCreateSerializer(
            data=request.data, context={'opportunity': opportunity, 'request': request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                application = serializer.save(candidate=profile, opportunity=opportunity)
        except IntegrityError:
            raise ValidationError({"detail": "Vous avez déjà postulé à cette opportunité."})

        return Response(ApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class MyApplicationListView(generics.ListAPIView):
    """
    GET /api/v1/applications/
    Le candidat voit la liste de ses propres candidatures.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Application.objects.filter(candidate__user=self.request.user)


class ApplicationDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/applications/{id}/
    Consultable par le candidat propriétaire OU un membre de l'organisation concernée.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, (IsApplicationOwner | IsApplicationOrgMember)]
    queryset = Application.objects.all()


class OrganizationApplicationListView(generics.ListAPIView):
    """
    GET /api/v1/opportunities/{id}/applications/
    Une organisation consulte les candidatures reçues sur UNE de ses opportunités.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        opportunity = generics.get_object_or_404(Opportunity, pk=self.kwargs['pk'])
        is_member = OrganizationMember.objects.filter(
            organization=opportunity.organization, user=self.request.user
        ).exists()
        if not is_member:
            raise PermissionDenied("Vous n'êtes pas autorisé à consulter ces candidatures.")
        return Application.objects.filter(opportunity=opportunity)


class UpdateApplicationStatusView(APIView):
    """
    PATCH /api/v1/applications/{id}/status/
    Une organisation fait progresser le statut d'une candidature reçue.
    """
    permission_classes = [permissions.IsAuthenticated, IsApplicationOrgMember]

    def patch(self, request, pk):
        application = generics.get_object_or_404(Application, pk=pk)
        self.check_object_permissions(request, application)

        serializer = ApplicationStatusUpdateSerializer(application, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ApplicationSerializer(application).data)


class WithdrawApplicationView(APIView):
    """
    POST /api/v1/applications/{id}/withdraw/
    Le candidat retire sa propre candidature.
    """
    permission_classes = [permissions.IsAuthenticated, IsApplicationOwner]

    def post(self, request, pk):
        application = generics.get_object_or_404(Application, pk=pk)
        self.check_object_permissions(request, application)

        if application.status in [Application.Status.ACCEPTED, Application.Status.REJECTED]:
            return Response(
                {"detail": "Cette candidature ne peut plus être retirée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = Application.Status.WITHDRAWN
        application.save()
        return Response(ApplicationSerializer(application).data)