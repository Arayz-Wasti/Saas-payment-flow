from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

def home(request):
    """Serve the home page."""
    return render(request, 'frontend/index.html')

def login_view(request):
    """Serve the login page."""
    return render(request, 'frontend/login.html')

def register_view(request):
    """Serve the register page."""
    return render(request, 'frontend/register.html')

def dashboard_view(request):
    """Serve the dashboard page."""
    return render(request, 'frontend/dashboard.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Landing page for the SaaS Payment API.
    Lists all available endpoints discovered from the URL configuration.
    """
    endpoints = {
        "users": {
            "register": reverse('register', request=request, format=format),
            "login": reverse('token_obtain_pair', request=request, format=format),
            "refresh_token": reverse('token_refresh', request=request, format=format),
            "profile": reverse('user_profile', request=request, format=format),
        },
        "subscriptions": {
            "plans": reverse('plan_list', request=request, format=format),
            "status": reverse('subscription_status', request=request, format=format),
            "verify": reverse('verify_checkout', request=request, format=format),
        },
        "payments": {
            "checkout": reverse('create_checkout_session', request=request, format=format),
            "portal": reverse('billing_portal', request=request, format=format),
            "webhook": request.build_absolute_uri('/api/payments/webhook/'),
        },
        "dashboard": {
            "premium_data": reverse('premium_dashboard', request=request, format=format),
        },
        "admin": request.build_absolute_uri('/admin/'),
    }
    
    return Response({
        "message": "Welcome to the SaaS Payment API",
        "version": "1.0.0",
        "endpoints": endpoints
    })
