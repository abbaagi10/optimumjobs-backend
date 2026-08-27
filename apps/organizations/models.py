from django.conf import settings
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Propriétaire'
        MANAGER = 'manager', 'Gestionnaire'
        RECRUITER = 'recruiter', 'Recruteur'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RECRUITER)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'user'],
                name='unique_organization_member',
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"