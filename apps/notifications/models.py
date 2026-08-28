from django.conf import settings
from django.db import models


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        APPLICATION_SUBMITTED = 'application_submitted', 'Candidature envoyée'
        APPLICATION_STATUS_CHANGED = 'application_status_changed', 'Statut de candidature modifié'
        OPPORTUNITY_APPROVED = 'opportunity_approved', 'Opportunité approuvée'
        OPPORTUNITY_REJECTED = 'opportunity_rejected', 'Opportunité rejetée'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name='destinataire',
    )
    notification_type = models.CharField('type', max_length=40, choices=NotificationType.choices)
    message = models.CharField('message', max_length=255)

    is_read = models.BooleanField('lue', default=False)

    created_at = models.DateTimeField('date de création', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'notification'
        verbose_name_plural = 'notifications'
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.recipient.email} - {self.message}"