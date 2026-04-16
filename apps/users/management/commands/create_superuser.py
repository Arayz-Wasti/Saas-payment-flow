import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


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

        # Guard against running before migrations have created the table.
        table_exists = 'users_customuser' in connection.introspection.table_names()

        if table_exists:
            # Delete any existing user with this email so we always start fresh.
            deleted_count, _ = User.objects.filter(email=email).delete()
            if deleted_count:
                self.stdout.write(
                    self.style.WARNING(f'Deleted {deleted_count} existing user(s) with email "{email}".')
                )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Table "users_customuser" does not exist yet — skipping delete step. '
                    'Run migrations first to create the table.'
                )
            )

        try:
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{email}" created successfully.')
            )
        except Exception as exc:
            raise CommandError(f'Failed to create superuser: {exc}') from exc
