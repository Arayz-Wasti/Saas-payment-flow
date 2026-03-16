"""WSGI config for SaaS Payment project."""
import os
from . import monkeypatch
monkeypatch.apply_patches()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
