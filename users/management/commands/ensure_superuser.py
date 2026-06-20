import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a superuser from env vars if it doesn't exist."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
