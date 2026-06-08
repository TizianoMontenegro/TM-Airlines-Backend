"""
Management command to create a TM-RAG service user and generate a long-lived JWT.

Usage:
    python manage.py create_rag_service_user
    python manage.py create_rag_service_user --username rag-service
"""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a service user for TM-RAG integration and outputs a long-lived JWT."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="rag-service@tm-airlines.internal")
        parser.add_argument("--days", type=int, default=365)

    def handle(self, *args, **options):
        username = options["username"]
        days = options["days"]

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": username,
                "is_active": True,
                "is_staff": False,
            },
        )

        if created:
            user.set_unusable_password()
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created service user: {username}"))
        else:
            self.stdout.write(f"Service user already exists: {username}")

        # Generate long-lived JWT
        refresh = RefreshToken.for_user(user)
        refresh.set_exp(lifetime=timedelta(days=days))
        access = refresh.access_token
        access.set_exp(lifetime=timedelta(days=days))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("TM-RAG SERVICE JWT (set as TM_RAG_API_KEY in TM-RAG .env):")
        self.stdout.write("=" * 60)
        self.stdout.write(str(access))
        self.stdout.write("=" * 60)
        self.stdout.write(f"\nToken expires in {days} days.")
        self.stdout.write("\nIf you lose this token, run this command again to generate a new one.")
        self.stdout.write("The old token will remain valid until its expiry.")
