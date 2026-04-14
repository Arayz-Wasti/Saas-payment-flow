web: python manage.py collectstatic --noinput && gunicorn config.wsgi:application --workers 1 --bind 0.0.0.0:$PORT --timeout 120 --log-level warning
release: python manage.py migrate && python manage.py createsuperuser --noinput || true
