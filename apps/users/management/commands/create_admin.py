from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Crée un superutilisateur par défaut si aucun n'existe encore avec cet email."

    def handle(self, *args, **options):
        User = get_user_model()
        email = "admin@admin.com"
        password = "Qw1234567890"

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Superutilisateur '{email}' existe déjà."))
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superutilisateur '{email}' créé."))