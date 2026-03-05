from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Plan, Subscription
from .services import SubscriptionService

User = get_user_model()

class SubscriptionTests(TestCase):
    """Test subscription model logic and services."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email='subscriber@example.com',
            password='password123'
        )
        self.plan = Plan.objects.create(
            name='Pro Monthly',
            stripe_price_id='price_123',
            price=29.99,
            interval='month',
            trial_days=7
        )

    def test_subscription_validity(self) -> None:
        """Test the is_valid property of Subscription."""
        now = timezone.now()
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            stripe_subscription_id='sub_123',
            status='active',
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )
        self.assertTrue(subscription.is_valid)

        # Expired
        subscription.current_period_end = now - timedelta(days=1)
        subscription.save()
        self.assertFalse(subscription.is_valid)

    def test_sync_subscription_status_service(self) -> None:
        """Test that SubscriptionService syncs user membership flags."""
        now = timezone.now()
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            stripe_subscription_id='sub_456',
            status='active',
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )
        
        # Initially False
        self.assertFalse(self.user.is_active_subscriber)
        
        # Sync
        SubscriptionService.sync_subscription_status(subscription)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active_subscriber)

        # Make invalid and sync
        subscription.status = 'expired'
        subscription.save()
        SubscriptionService.sync_subscription_status(subscription)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active_subscriber)
