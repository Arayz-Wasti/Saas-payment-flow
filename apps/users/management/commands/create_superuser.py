import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create or replace the superuser from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')

        if not email:
            raise CommandError('DJANGO_SUPERUSER_EMAIL environment variable is not set.')
        if not password:
            raise CommandError('DJANGO_SUPERUSER_PASSWORD environment variable is not set.')

        # Delete any existing user with this email so we always start fresh.
        deleted_count, _ = User.objects.filter(email=email).delete()
        if deleted_count:
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing user(s) with email "{email}".')
            )

        try:
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{email}" created successfully.')
            )
        except Exception as exc:
            raise CommandError(f'Failed to create superuser: {exc}') from exc
