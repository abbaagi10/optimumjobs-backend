import os
import puremagic
from django.conf import settings
from django.core.exceptions import ValidationError
def validate_file_size(file):
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file.size > max_size:
        raise ValidationError(
            f"Le fichier dépasse la taille maximale autorisée ({settings.MAX_UPLOAD_SIZE_MB} Mo)."
        )
def validate_file_extension(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in settings.ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(
            f"Extension de fichier non autorisée. Extensions acceptées : "
            f"{', '.join(settings.ALLOWED_DOCUMENT_EXTENSIONS)}."
        )
def validate_file_mime_type(file):
    file.seek(0)
    file_head = file.read(2048)
    file.seek(0)
    try:
        detected_mime = puremagic.from_string(file_head, mime=True)
    except puremagic.PureError:
        detected_mime = None
    if detected_mime not in settings.ALLOWED_DOCUMENT_MIME_TYPES:
        raise ValidationError(
            f"Type de fichier non autorisé (détecté : {detected_mime}). "
            f"Le contenu réel du fichier ne correspond pas à un format accepté."
        )