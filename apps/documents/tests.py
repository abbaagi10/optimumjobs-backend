from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Document

User = get_user_model()

# Signature binaire minimale d'un PDF valide (suffisante pour que python-magic
# détecte correctement le type MIME "application/pdf").
MINIMAL_PDF_CONTENT = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"


class DocumentUploadTests(APITestCase):
    """Tests de validation à l'upload : taille, extension, type MIME réel."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='candidat@test.com', password='MotDePasseSolide123', role='candidate',
        )
        self.client.force_authenticate(user=self.user)

    def test_upload_valid_pdf_succeeds(self):
        """Un vrai PDF, avec une extension .pdf, est accepté."""
        file = SimpleUploadedFile('cv.pdf', MINIMAL_PDF_CONTENT, content_type='application/pdf')

        response = self.client.post('/api/v1/documents/', {
            'document_type': 'cv',
            'file': file,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['mime_type'], 'application/pdf')

    def test_upload_forbidden_extension_rejected(self):
        """
        TEST CRITIQUE : un fichier avec une extension interdite (.exe) est rejeté,
        même si son contenu réel n'a rien de dangereux.
        """
        file = SimpleUploadedFile('malware.exe', b'contenu quelconque', content_type='application/octet-stream')

        response = self.client.post('/api/v1/documents/', {
            'document_type': 'cv',
            'file': file,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_fake_pdf_with_wrong_content_rejected(self):
        """
        TEST CRITIQUE : un fichier renommé en .pdf mais dont le contenu réel
        n'est pas un PDF est rejeté par la vérification MIME (python-magic).
        Simule une tentative de contournement de la validation par extension seule.
        """
        file = SimpleUploadedFile('cv.pdf', b'Ceci est en fait du texte brut, pas un PDF', content_type='application/pdf')

        response = self.client.post('/api/v1/documents/', {
            'document_type': 'cv',
            'file': file,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_uploaded_file_url_not_exposed_in_response(self):
        """
        TEST CRITIQUE : la réponse ne doit jamais contenir d'URL directe vers le fichier
        (voir la correction de sécurité faite en Étape 9).
        """
        file = SimpleUploadedFile('cv.pdf', MINIMAL_PDF_CONTENT, content_type='application/pdf')

        response = self.client.post('/api/v1/documents/', {
            'document_type': 'cv',
            'file': file,
        }, format='multipart')

        self.assertNotIn('file', response.data)


class DocumentAccessTests(APITestCase):
    """Tests d'accès sécurisé aux documents (téléchargement contrôlé)."""

    def setUp(self):
        self.owner = User.objects.create_user(
            email='proprietaire@test.com', password='MotDePasseSolide123', role='candidate',
        )
        self.other_user = User.objects.create_user(
            email='autre@test.com', password='MotDePasseSolide123', role='candidate',
        )

        self.client.force_authenticate(user=self.owner)
        file = SimpleUploadedFile('cv.pdf', MINIMAL_PDF_CONTENT, content_type='application/pdf')
        response = self.client.post('/api/v1/documents/', {'document_type': 'cv', 'file': file}, format='multipart')
        self.document_id = response.data['id']

    def test_owner_can_download_own_document(self):
        """Le propriétaire peut télécharger son propre document."""
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(f'/api/v1/documents/{self.document_id}/download/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_download_document(self):
        """
        TEST CRITIQUE : un autre utilisateur ne peut pas télécharger un document
        qui ne lui appartient pas, et reçoit un 404 (pas 403, voir Étape 9).
        """
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(f'/api/v1/documents/{self.document_id}/download/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_cannot_download_document(self):
        """Sans authentification, aucun accès au téléchargement."""
        self.client.force_authenticate(user=None)

        response = self.client.get(f'/api/v1/documents/{self.document_id}/download/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_document_returns_404(self):
        """Un ID de document inexistant renvoie 404, sans lever d'exception serveur."""
        self.client.force_authenticate(user=self.owner)

        response = self.client.get('/api/v1/documents/999999/download/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)