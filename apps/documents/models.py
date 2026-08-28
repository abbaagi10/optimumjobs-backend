import os
import uuid

from django.conf import settings
from django.db import models

from .validators import validate_file_size, validate_file_extension, validate_file_mime_type


def document_upload_path(instance, filename):
    """
    Génère un chemin de stockage qui ne révèle rien sur le contenu ou le propriétaire,
    et évite les collisions de noms de fichiers entre utilisateurs différents.
    """
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    return os.path.join('documents', str(instance.owner_id), new_filename)


class Document(models.Model):
    class DocumentType(models.TextChoices):
        CV = 'cv', 'CV'
        DIPLOMA = 'diploma', 'Diplôme'
        CERTIFICATE = 'certificate', 'Certificat'
        COVER_LETTER = 'cover_letter', 'Lettre de motivation'
        OTHER = 'other', 'Autre'

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents', verbose_name='propriétaire',
    )
    document_type = models.CharField('type', max_length=20, choices=DocumentType.choices)

    file = models.FileField(
        'fichier',
        upload_to=document_upload_path,
        validators=[validate_file_size, validate_file_extension, validate_file_mime_type],
    )
    original_filename = models.CharField('nom original', max_length=255)
    file_size = models.PositiveIntegerField('taille (octets)')
    mime_type = models.CharField('type MIME', max_length=100)

    uploaded_at = models.DateTimeField("date d'upload", auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'document'
        verbose_name_plural = 'documents'

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.owner.email}"