from django.urls import path
from .views import PremiumDashboardView

urlpatterns = [
    path('premium-data/', PremiumDashboardView.as_view(), name='premium_dashboard'),
]
