import os
import django
import stripe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from apps.subscriptions.models import Plan

stripe.api_key = settings.STRIPE_SECRET_KEY


def setup_stripe_products():
    """Create Stripe products/prices and sync them to the local Plan table."""
    print("Setting up Stripe Products and Prices...")

    # 1. Hobby Plan
    hobby_product = stripe.Product.create(
        name="Hobby Plan",
        description="Up to 1,000 users, Basic Analytics, 24-hour support."
    )
    hobby_price = stripe.Price.create(
        product=hobby_product.id,
        unit_amount=900,  # $9.00
        currency="usd",
        recurring={"interval": "month"},
    )

    Plan.objects.update_or_create(
        name="Hobby",
        defaults={
            "stripe_product_id": hobby_product.id,
            "stripe_price_id": hobby_price.id,
            "description": "Hobby tier for starters",
            "price": 9.00,
            "currency": "usd",
            "interval": "month",
            "is_active": True,
        }
    )
    print(f"Hobby Plan configured: {hobby_price.id}")

    # 2. Pro Plan
    pro_product = stripe.Product.create(
        name="Pro Plan",
        description="Unlimited users, Advanced Analytics, 1-hour support SLA."
    )
    pro_price = stripe.Price.create(
        product=pro_product.id,
        unit_amount=2900,  # $29.00
        currency="usd",
        recurring={"interval": "month"},
    )

    Plan.objects.update_or_create(
        name="Pro",
        defaults={
            "stripe_product_id": pro_product.id,
            "stripe_price_id": pro_price.id,
            "description": "Pro tier for growing businesses",
            "price": 29.00,
            "currency": "usd",
            "interval": "month",
            "trial_days": 7,
            "is_active": True,
        }
    )
    print(f"Pro Plan configured: {pro_price.id}")

    print("Stripe setup complete!")


if __name__ == "__main__":
    setup_stripe_products()
