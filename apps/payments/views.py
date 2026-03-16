import stripe
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework import status, views, permissions
from rest_framework.response import Response

from apps.subscriptions.models import Plan, Subscription
from apps.subscriptions.services import SubscriptionService
from .services import StripeService

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()


class CreateCheckoutSessionView(views.APIView):
    """
    Endpoint to create a Stripe Checkout Session for a plan.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'error': 'plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
            
            # Stripe requires absolute URLs
            success_url = request.build_absolute_uri('/dashboard/') + "?session_id={CHECKOUT_SESSION_ID}"
            cancel_url = request.build_absolute_uri('/#pricing')

            checkout_url = StripeService.create_checkout_session(
                user=request.user,
                plan=plan,
                success_url=success_url,
                cancel_url=cancel_url
            )
            return Response({'checkout_url': checkout_url})
        except Plan.DoesNotExist:
            return Response({'error': 'Invalid plan_id'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyCheckoutView(views.APIView):
    """
    After Stripe redirects back, the frontend calls this endpoint
    with the session_id to verify the payment and activate the subscription.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'session_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status != 'paid':
                return Response({'error': 'Payment not completed'}, status=status.HTTP_400_BAD_REQUEST)

            stripe_sub_id = session.subscription
            if not stripe_sub_id:
                return Response({'error': 'No subscription found in session'}, status=status.HTTP_400_BAD_REQUEST)

            stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)

            # Find plan by matching the stripe_price_id
            stripe_price_id = stripe_sub['items']['data'][0]['price']['id']
            try:
                plan = Plan.objects.get(stripe_price_id=stripe_price_id)
            except Plan.DoesNotExist:
                return Response({'error': 'Plan not found for this price'}, status=status.HTTP_400_BAD_REQUEST)

            # Create or update the subscription
            sub, created = Subscription.objects.update_or_create(
                user=request.user,
                defaults={
                    'plan': plan,
                    'stripe_subscription_id': stripe_sub_id,
                    'status': stripe_sub.status,
                    'current_period_start': timezone.make_aware(
                        datetime.datetime.fromtimestamp(stripe_sub.current_period_start)
                    ),
                    'current_period_end': timezone.make_aware(
                        datetime.datetime.fromtimestamp(stripe_sub.current_period_end)
                    ),
                }
            )

            # Mark user as active subscriber
            request.user.is_active_subscriber = True
            request.user.save(update_fields=['is_active_subscriber'])

            return Response({
                'status': 'success',
                'subscription': {
                    'plan_name': plan.name,
                    'price': str(plan.price),
                    'status': sub.status,
                    'current_period_end': sub.current_period_end.isoformat(),
                }
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionStatusView(views.APIView):
    """
    Returns current subscription status for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            sub = request.user.subscription
            return Response({
                'has_subscription': True,
                'plan_name': sub.plan.name,
                'plan_price': str(sub.plan.price),
                'status': sub.status,
                'is_valid': sub.is_valid,
                'current_period_start': sub.current_period_start.isoformat(),
                'current_period_end': sub.current_period_end.isoformat(),
                'cancel_at_period_end': sub.cancel_at_period_end,
            })
        except Subscription.DoesNotExist:
            return Response({
                'has_subscription': False,
                'plan_name': None,
                'status': 'none',
                'is_valid': False,
            })


class BillingPortalView(views.APIView):
    """
    Endpoint to create a Stripe Billing Portal session.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            return_url = request.build_absolute_uri('/dashboard/')
            portal_url = StripeService.create_billing_portal_session(
                user=request.user,
                return_url=return_url
            )
            return Response({'portal_url': portal_url})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(views.APIView):
    """
    Handle Stripe Webhooks.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'invoice.paid':
            invoice = event['data']['object']
            self._handle_invoice_paid(invoice)

        elif event['type'] == 'customer.subscription.deleted':
            stripe_subscription = event['data']['object']
            self._handle_subscription_deleted(stripe_subscription)

        return HttpResponse(status=status.HTTP_200_OK)

    def _handle_invoice_paid(self, invoice):
        stripe_sub_id = invoice.get('subscription')
        if not stripe_sub_id:
            return
        stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
        try:
            sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
            sub.current_period_start = timezone.make_aware(
                datetime.datetime.fromtimestamp(stripe_sub.current_period_start)
            )
            sub.current_period_end = timezone.make_aware(
                datetime.datetime.fromtimestamp(stripe_sub.current_period_end)
            )
            sub.status = stripe_sub.status
            sub.save()
            SubscriptionService.sync_subscription_status(sub)
        except Subscription.DoesNotExist:
            pass

    def _handle_subscription_deleted(self, stripe_subscription):
        stripe_sub_id = stripe_subscription.get('id')
        try:
            sub = Subscription.objects.get(stripe_subscription_id=stripe_sub_id)
            SubscriptionService.handle_cancellation(sub)
        except Subscription.DoesNotExist:
            pass
