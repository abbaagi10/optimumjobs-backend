# apps/documents/views.py
# C:\optimumjobs-backend\apps\documents\views.py

import os

from django.http import FileResponse, Http404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .permissions import IsDocumentOwner
from .serializers import DocumentSerializer


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/v1/documents/{id}/    -> métadonnées (pas le fichier lui-même)
    DELETE /api/v1/documents/{id}/    -> suppression (bloquée si utilisé dans une candidature, via PROTECT)
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDocumentOwner]
    queryset = Document.objects.all()


class DocumentDownloadView(APIView):
    """
    GET /api/v1/documents/{id}/download/
    Sert le fichier réel, après vérification stricte des droits d'accès.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return Response(
                {"detail": "Document non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not self._can_access(request.user, document):
            return Response(
                {"detail": "Vous n'êtes pas autorisé à accéder à ce document."},
                status=status.HTTP_403_FORBIDDEN
            )

        if not document.file or not os.path.exists(document.file.path):
            return Response(
                {"detail": "Le fichier n'existe pas."},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.original_filename,
        )

    def _can_access(self, user, document):
        # ✅ 1. Le propriétaire peut accéder
        if document.owner == user:
            return True
        
        # ✅ 2. Les administrateurs peuvent accéder
        if user.is_staff:
            return True
        
        # ✅ 3. Un membre de l'organisation peut accéder si ce document
        # est utilisé dans une candidature reçue sur une de ses offres.
        from apps.organizations.models import OrganizationMember
        from apps.applications.models import ApplicationDocument
        from apps.applications.models import Application
        from apps.opportunities.models import Opportunity
        
        # Vérifier si le document est lié à une candidature
        app_docs = ApplicationDocument.objects.filter(document=document)
        
        if app_docs.exists():
            # Récupérer les IDs des applications
            app_ids = app_docs.values_list('application_id', flat=True)
            
            # Récupérer les IDs des opportunités liées à ces applications
            opp_ids = Application.objects.filter(id__in=app_ids).values_list('opportunity_id', flat=True)
            
            # Récupérer les IDs des organisations liées à ces opportunités
            org_ids = Opportunity.objects.filter(id__in=opp_ids).values_list('organization_id', flat=True)
            
            # Vérifier si l'utilisateur est membre d'une de ces organisations
            has_access = OrganizationMember.objects.filter(
                user=user,
                organization_id__in=org_ids
            ).exists()
            
            if has_access:
                return True
        
        # ❌ Refuser l'accès
        return False