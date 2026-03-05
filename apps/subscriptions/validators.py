from django.utils import timezone
from apps.subscriptions.models import Subscription

class SubscriptionValidator:
    """
    Utility to check subscription validity for a user.
    """
    @staticmethod
    def has_active_subscription(user) -> bool:
        """
        Returns True if user has an active/trialing subscription that hasn't expired.
        """
        if not user.is_authenticated:
            return False
            
        try:
            subscription = user.subscription
            return subscription.is_valid
        except Subscription.DoesNotExist:
            return False
