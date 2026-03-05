from rest_framework import permissions
from apps.subscriptions.validators import SubscriptionValidator

class IsSubscribed(permissions.BasePermission):
    """
    Custom permission to only allow access to subscribers.
    """
    message = 'You must have an active subscription to access this resource.'

    def has_permission(self, request, view):
        return SubscriptionValidator.has_active_subscription(request.user)
