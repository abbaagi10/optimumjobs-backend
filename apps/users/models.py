# apps/users/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserRole(models.TextChoices):
    CANDIDATE = 'candidate', 'Candidat'
    ORGANIZATION = 'organization', 'Organisation'
    ADMIN = 'admin', 'Administrateur'


class UserManager(BaseUserManager):
    """
    Manager personnalisé : sait comment créer un utilisateur normal
    et un superutilisateur, en utilisant l'email au lieu du username.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Champs d'authentification
    email = models.EmailField('adresse email', unique=True)
    role = models.CharField('rôle', max_length=20, choices=UserRole.choices, default=UserRole.CANDIDATE)

    # Champs de profil (AJOUTÉS)
    first_name = models.CharField('prénom', max_length=150, blank=True, null=True)
    last_name = models.CharField('nom', max_length=150, blank=True, null=True)
    phone = models.CharField('téléphone', max_length=20, blank=True, null=True)
    city = models.CharField('ville', max_length=100, blank=True, null=True)
    country = models.CharField('pays', max_length=100, blank=True, null=True)
    bio = models.TextField('biographie', blank=True, null=True)

    # Champs de statut
    is_active = models.BooleanField('actif', default=True)
    is_staff = models.BooleanField('membre du staff', default=False)

    # Champs de date
    created_at = models.DateTimeField('date de création', auto_now_add=True)
    updated_at = models.DateTimeField('date de mise à jour', auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'utilisateur'
        verbose_name_plural = 'utilisateurs'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_short_name(self):
        """Retourne le prénom ou l'email."""
        return self.first_name or self.email