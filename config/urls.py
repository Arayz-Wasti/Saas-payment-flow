"""URL configuration for SaaS Payment project."""
from django.contrib import admin
from django.urls import include, path

urlpatterns: list = [
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/subscriptions/', include('apps.subscriptions.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
]
