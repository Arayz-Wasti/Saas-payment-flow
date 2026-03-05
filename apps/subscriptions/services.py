from django.utils import timezone
from .models import Subscription


class SubscriptionService:
    """
    Helper service for subscription-related business logic.
    """

    @staticmethod
    def sync_subscription_status(subscription: Subscription) -> bool:
        """
        Updates the user's membership flag based on subscription validity.
        """
        is_valid = subscription.is_valid
        user = subscription.user
        
        if user.is_active_subscriber != is_valid:
            user.is_active_subscriber = is_valid
            user.save(update_fields=['is_active_subscriber'])
            return True
        return False

    @staticmethod
    def handle_cancellation(subscription: Subscription) -> None:
        """
        Processes a subscription cancellation.
        """
        subscription.status = 'canceled'
        subscription.canceled_at = timezone.now()
        subscription.save()
        SubscriptionService.sync_subscription_status(subscription)
