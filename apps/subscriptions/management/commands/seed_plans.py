from django.core.management.base import BaseCommand
from django.conf import settings
from apps.subscriptions.models import Plan
import stripe

class Command(BaseCommand):
    help = 'Seed subscription plans and sync with Stripe'

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        self.stdout.write("Seeding plans...")
        
        plans_data = [
            {
                "name": "Hobby",
                "price": 9.00,
                "interval": "month",
                "description": "Up to 1,000 users, Basic Analytics, 24-hour support.",
                "features": {
                    "users": "Up to 1,000 users",
                    "analytics": "Basic Analytics",
                    "support": "24-hour support"
                }
            },
            {
                "name": "Pro",
                "price": 29.00,
                "interval": "month",
                "description": "Unlimited users, Advanced Analytics, 1-hour support SLA.",
                "trial_days": 7,
                "features": {
                    "users": "Unlimited users",
                    "analytics": "Advanced Analytics",
                    "support": "1-hour support SLA",
                    "integrations": "Custom integrations"
                }
            }
        ]

        for data in plans_data:
            plan, created = Plan.objects.get_or_create(
                name=data["name"],
                defaults={
                    "price": data["price"],
                    "interval": data["interval"],
                    "description": data["description"],
                    "features": data["features"],
                    "trial_days": data.get("trial_days", 0),
                    "is_active": True
                }
            )
            
            if not plan.stripe_price_id:
                self.stdout.write(f"Creating Stripe product for {plan.name}...")
                product = stripe.Product.create(
                    name=f"SaaSFlow {plan.name} Plan",
                    description=plan.description
                )
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(plan.price * 100),
                    currency="usd",
                    recurring={"interval": plan.interval},
                )
                plan.stripe_product_id = product.id
                plan.stripe_price_id = price.id
                plan.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully synced {plan.name} with Stripe: {price.id}"))
            else:
                self.stdout.write(f"Plan {plan.name} already synced with Stripe.")

        self.stdout.write(self.style.SUCCESS("Plan seeding complete."))
