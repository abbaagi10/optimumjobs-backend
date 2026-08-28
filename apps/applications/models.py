from django.db import models

from apps.profiles.models import CandidateProfile
from apps.opportunities.models import Opportunity


class Application(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Envoyée'
        UNDER_REVIEW = 'under_review', 'En cours d\'examen'
        SHORTLISTED = 'shortlisted', 'Présélectionnée'
        INTERVIEW = 'interview', 'Entretien proposé'
        ACCEPTED = 'accepted', 'Acceptée'
        REJECTED = 'rejected', 'Refusée'
        WITHDRAWN = 'withdrawn', 'Retirée'

    candidate = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name='applications', verbose_name='candidat',
    )
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name='applications', verbose_name='opportunité',
    )

    status = models.CharField('statut', max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    cover_note = models.TextField('message de motivation', blank=True)

    submitted_at = models.DateTimeField('date de candidature', auto_now_add=True)
    updated_at = models.DateTimeField('date de mise à jour', auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'candidature'
        verbose_name_plural = 'candidatures'
        constraints = [
            models.UniqueConstraint(
                fields=['candidate', 'opportunity'],
                name='unique_application_per_candidate_opportunity',
            )
        ]
        indexes = [
            models.Index(fields=['opportunity', 'status']),
        ]

    def __str__(self):
        return f"{self.candidate.user.email} -> {self.opportunity.title}"

from apps.documents.models import Document


class ApplicationDocument(models.Model):
    """
    Référence stable vers un document utilisé au moment d'une candidature.
    Ne change jamais après création, même si le candidat modifie ses documents plus tard.
    """
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='documents', verbose_name='candidature',
    )
    document = models.ForeignKey(
        Document, on_delete=models.PROTECT, related_name='application_documents', verbose_name='document',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['application', 'document'],
                name='unique_document_per_application',
            )
        ]
        verbose_name = 'document de candidature'
        verbose_name_plural = 'documents de candidature'

    def __str__(self):
        return f"{self.application} - {self.document}"
    