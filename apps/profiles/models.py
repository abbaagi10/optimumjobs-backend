from django.conf import settings
from django.db import models

from apps.core.models import Skill


class CandidateProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_profile',
        verbose_name='utilisateur',
    )

    first_name = models.CharField('prénom', max_length=100, blank=True)
    last_name = models.CharField('nom', max_length=100, blank=True)
    phone = models.CharField('téléphone', max_length=30, blank=True)
    city = models.CharField('ville', max_length=100, blank=True)
    country = models.CharField('pays', max_length=100, blank=True)
    bio = models.TextField('biographie', blank=True)

    skills = models.ManyToManyField(Skill, blank=True, related_name='candidate_profiles', verbose_name='compétences')

    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de mise à jour', auto_now=True)

    class Meta:
        verbose_name = 'profil candidat'
        verbose_name_plural = 'profils candidats'

    def __str__(self):
        return f"Profil de {self.user.email}"


class Experience(models.Model):
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='experiences',
        verbose_name='profil',
    )

    title = models.CharField('intitulé du poste', max_length=150)
    company = models.CharField('entreprise', max_length=150)
    location = models.CharField('lieu', max_length=150, blank=True)
    start_date = models.DateField('date de début')
    end_date = models.DateField('date de fin', null=True, blank=True)
    is_current = models.BooleanField('poste actuel', default=False)
    description = models.TextField('description', blank=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'expérience professionnelle'
        verbose_name_plural = 'expériences professionnelles'

    def __str__(self):
        return f"{self.title} chez {self.company}"


class Education(models.Model):
    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='education',
        verbose_name='profil',
    )

    degree = models.CharField('diplôme', max_length=150)
    institution = models.CharField('établissement', max_length=150)
    field_of_study = models.CharField("domaine d'étude", max_length=150, blank=True)
    start_date = models.DateField('date de début')
    end_date = models.DateField('date de fin', null=True, blank=True)
    is_current = models.BooleanField('en cours', default=False)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'formation'
        verbose_name_plural = 'formations'

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Language(models.Model):
    class Level(models.TextChoices):
        BASIC = 'basic', 'Notions'
        INTERMEDIATE = 'intermediate', 'Intermédiaire'
        FLUENT = 'fluent', 'Courant'
        NATIVE = 'native', 'Langue maternelle'

    profile = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='languages',
        verbose_name='profil',
    )

    name = models.CharField('langue', max_length=100)
    level = models.CharField('niveau', max_length=20, choices=Level.choices)

    class Meta:
        unique_together = ('profile', 'name')
        verbose_name = 'langue'
        verbose_name_plural = 'langues'

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"