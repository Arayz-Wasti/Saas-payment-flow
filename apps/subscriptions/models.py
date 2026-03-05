from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    """
    Represents a subscription plan (e.g., Monthly, Yearly).
    """
    INTERVAL_CHOICES = (
        ('month', 'Monthly'),
        ('year', 'Yearly'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    stripe_product_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    trial_days = models.IntegerField(default=0)
    features = models.JSONField(default=dict, help_text="JSON object of features included in this plan.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.interval})"


class Subscription(models.Model):
    """
    Connects a User to a Plan via Stripe.
    """
    STATUS_CHOICES = (
        ('trialing', 'Trialing'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
        ('expired', 'Expired'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.email} - {self.plan.name}"

    @property
    def is_valid(self) -> bool:
        """Checks if the subscription is currently active or in trial."""
        if self.status in ['active', 'trialing']:
            return self.current_period_end > timezone.now()
        return False
