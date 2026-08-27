from django.conf import settings
from django.db import models

from apps.core.models import Skill
from apps.organizations.models import Organization


class Category(models.Model):
    """
    Catégorie métier d'une opportunité (ex: "Informatique", "Comptabilité").
    Séparée de Skill : une catégorie classe l'opportunité, une compétence
    décrit une capacité technique précise. Les deux sont utiles pour filtrer.
    """
    name = models.CharField('nom', max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'catégorie'
        verbose_name_plural = 'catégories'

    def __str__(self):
        return self.name


class Opportunity(models.Model):
    class OpportunityType(models.TextChoices):
        JOB = 'job', 'Emploi'
        INTERNSHIP = 'internship', 'Stage'
        TRAINING = 'training', 'Formation'

    class ExperienceLevel(models.TextChoices):
        ENTRY = 'entry', 'Débutant'
        JUNIOR = 'junior', 'Junior'
        SENIOR = 'senior', 'Senior'
        EXPERT = 'expert', 'Expert'

    class EducationLevel(models.TextChoices):
        HIGH_SCHOOL = 'high_school', 'Baccalauréat'
        BACHELOR = 'bachelor', 'Licence'
        MASTER = 'master', 'Master'
        DOCTORATE = 'doctorate', 'Doctorat'

    class ContractType(models.TextChoices):
        CDI = 'cdi', 'CDI'
        CDD = 'cdd', 'CDD'
        FREELANCE = 'freelance', 'Freelance'
        NOT_APPLICABLE = 'n_a', 'Non applicable'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        PENDING_REVIEW = 'pending_review', 'En attente de validation'
        APPROVED = 'approved', 'Approuvée'
        PUBLISHED = 'published', 'Publiée'
        REJECTED = 'rejected', 'Rejetée'
        CLOSED = 'closed', 'Clôturée'
        ARCHIVED = 'archived', 'Archivée'

    # --- Relations ---
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='opportunities', verbose_name='organisation',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='opportunities', verbose_name='catégorie',
    )
    skills = models.ManyToManyField(Skill, blank=True, related_name='opportunities', verbose_name='compétences requises')

    # --- Champs communs ---
    title = models.CharField('titre', max_length=200)
    description = models.TextField('description')
    opportunity_type = models.CharField('type', max_length=20, choices=OpportunityType.choices)

    city = models.CharField('ville', max_length=100, blank=True)
    country = models.CharField('pays', max_length=100, blank=True)
    is_remote = models.BooleanField('télétravail', default=False)

    experience_level = models.CharField(
        "niveau d'expérience", max_length=20, choices=ExperienceLevel.choices, blank=True,
    )
    education_level = models.CharField(
        "niveau d'étude", max_length=20, choices=EducationLevel.choices, blank=True,
    )

    # --- Champs spécifiques (limités, comme discuté en analyse) ---
    contract_type = models.CharField(
        'type de contrat', max_length=20, choices=ContractType.choices, default=ContractType.NOT_APPLICABLE,
    )
    salary_min = models.PositiveIntegerField('salaire minimum', null=True, blank=True)
    salary_max = models.PositiveIntegerField('salaire maximum', null=True, blank=True)
    duration_weeks = models.PositiveIntegerField('durée (semaines)', null=True, blank=True)

    # --- Workflow ---
    status = models.CharField('statut', max_length=20, choices=Status.choices, default=Status.DRAFT)
    rejection_reason = models.TextField('motif de rejet', blank=True)

    application_deadline = models.DateField("date limite de candidature", null=True, blank=True)
    published_at = models.DateTimeField('date de publication', null=True, blank=True)

    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de mise à jour', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'opportunité'
        verbose_name_plural = 'opportunités'
        indexes = [
            models.Index(fields=['status', 'opportunity_type']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_opportunity_type_display()})"