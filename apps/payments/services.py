import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.subscriptions.models import Plan, Subscription

User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Wrapper for Stripe SDK interactions.
    """

    @staticmethod
    def get_or_create_customer(user: User) -> str:
        """
        Retrieves or creates a Stripe Customer ID for a user.
        """
        if user.stripe_customer_id:
            return user.stripe_customer_id

        customer = stripe.Customer.create(
            email=user.email,
            metadata={'user_id': user.id}
        )
        user.stripe_customer_id = customer.id
        user.save(update_fields=['stripe_customer_id'])
        return customer.id

    @staticmethod
    def create_checkout_session(user: User, plan: Plan, success_url: str, cancel_url: str) -> str:
        """
        Creates a Stripe Checkout Session for a subscription.
        """
        customer_id = StripeService.get_or_create_customer(user)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            subscription_data={
                'metadata': {
                    'user_id': user.id,
                    'plan_id': plan.id,
                }
            },
        )
        return session.url

    @staticmethod
    def create_billing_portal_session(user: User, return_url: str) -> str:
        """
        Creates a Stripe Billing Portal session for a user.
        """
        customer_id = StripeService.get_or_create_customer(user)
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url
