from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    VerifyCheckoutView,
    SubscriptionStatusView,
    BillingPortalView,
    StripeWebhookView
)

urlpatterns = [
    path('checkout/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('verify-checkout/', VerifyCheckoutView.as_view(), name='verify_checkout'),
    path('subscription-status/', SubscriptionStatusView.as_view(), name='subscription_status'),
    path('portal/', BillingPortalView.as_view(), name='billing_portal'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
]
