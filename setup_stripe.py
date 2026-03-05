import os
import django
import stripe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from apps.subscriptions.models import Plan

stripe.api_key = settings.STRIPE_SECRET_KEY

def setup_stripe_products():
    print("Setting up Stripe Products and Prices...")
    
    # 1. Hobby Plan
    hobby_product = stripe.Product.create(
        name="Hobby Plan",
        description="Up to 1,000 users, Basic Analytics, 24-hour support."
    )
    hobby_price = stripe.Price.create(
        product=hobby_product.id,
        unit_amount=900, # $9.00
        currency="usd",
        recurring={"interval": "month"},
    )
    
    # Update DB
    Plan.objects.update_or_create(
        name="Hobby",
        defaults={
            "stripe_product_id": hobby_product.id,
            "stripe_price_id": hobby_price.id,
            "description": "Hobby tier for starters",
            "price": 9.00,
            "is_active": True
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
        unit_amount=2900, # $29.00
        currency="usd",
        recurring={"interval": "month"},
    )
    
    # Update DB
    Plan.objects.update_or_create(
        name="Pro",
        defaults={
            "stripe_product_id": pro_product.id,
            "stripe_price_id": pro_price.id,
            "description": "Pro tier for growing businesses",
            "price": 29.00,
            "is_active": True
        }
    )
    print(f"Pro Plan configured: {pro_price.id}")
    
    print("Stripe setup complete! Returning price IDs for frontend update.")
    return hobby_price.id, pro_price.id

if __name__ == "__main__":
    hobby_price_id, pro_price_id = setup_stripe_products()
    
    # Auto-update frontend HTML with new Stripe IDs for demonstration
    frontend_path = os.path.join(settings.BASE_DIR, 'frontend', 'index.html')
    if os.path.exists(frontend_path):
        with open(frontend_path, 'r') as f:
            content = f.read()
            
        # Very simple replace for the demo placeholders
        content = content.replace("'price_Hobby123Ex'", f"'{hobby_price_id}'")
        content = content.replace("'price_Pro123Ex'", f"'{pro_price_id}'")
        
        with open(frontend_path, 'w') as f:
            f.write(content)
        print("Updated frontend/index.html with new Stripe Price IDs.")
