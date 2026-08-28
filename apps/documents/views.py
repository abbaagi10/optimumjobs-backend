import os

from django.http import FileResponse, Http404
from rest_framework import generics, permissions
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
            raise Http404

        if not self._can_access(request.user, document):
            raise Http404  # on ne révèle même pas que le document existe

        if not document.file or not os.path.exists(document.file.path):
            raise Http404

        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.original_filename,
        )

    def _can_access(self, user, document):
        if document.owner == user:
            return True
        # Un membre de l'organisation peut accéder si ce document
        # est utilisé dans une candidature reçue sur une de ses offres.
        from apps.organizations.models import OrganizationMember
        return OrganizationMember.objects.filter(
            organization__opportunities__applications__documents__document=document,
            user=user,
        ).exists()