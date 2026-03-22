from typing import Optional, Dict, Any, List
import stripe
from config import settings


stripe.api_key = settings.stripe_secret_key


class StripeService:
    def __init__(self):
        self.webhook_secret = settings.stripe_webhook_secret

    async def create_customer(
        self,
        email: str,
        name: str,
        phone: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> stripe.Customer:
        try:
            customer_params = {
                "email": email,
                "name": name,
            }
            
            if phone:
                customer_params["phone"] = phone
            
            if metadata:
                customer_params["metadata"] = metadata
            
            customer = stripe.Customer.create(**customer_params)
            return customer
            
        except stripe.error.StripeError as e:
            print(f"Error creating customer: {e}")
            raise

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str
    ) -> stripe.Subscription:
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            return subscription
            
        except stripe.error.StripeError as e:
            print(f"Error creating subscription: {e}")
            raise

    async def cancel_subscription(
        self,
        subscription_id: str
    ) -> stripe.Subscription:
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return subscription
            
        except stripe.error.StripeError as e:
            print(f"Error canceling subscription: {e}")
            raise

    async def get_subscription(
        self,
        subscription_id: str
    ) -> stripe.Subscription:
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
            
        except stripe.error.StripeError as e:
            print(f"Error getting subscription: {e}")
            raise

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str
    ) -> stripe.checkout.Session:
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url
            )
            return session
            
        except stripe.error.StripeError as e:
            print(f"Error creating checkout session: {e}")
            raise

    async def construct_webhook_event(
        self,
        payload: bytes,
        signature: str
    ) -> stripe.Event:
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret
            )
            return event
            
        except stripe.error.StripeError as e:
            print(f"Error constructing webhook event: {e}")
            raise

    async def handle_subscription_created(
        self,
        subscription: stripe.Subscription
    ) -> Dict[str, Any]:
        try:
            customer_id = subscription.customer
            subscription_id = subscription.id
            status = subscription.status
            
            return {
                "customer_id": customer_id,
                "subscription_id": subscription_id,
                "status": status,
                "event": "subscription.created"
            }
            
        except Exception as e:
            print(f"Error handling subscription created: {e}")
            raise

    async def handle_subscription_updated(
        self,
        subscription: stripe.Subscription
    ) -> Dict[str, Any]:
        try:
            customer_id = subscription.customer
            subscription_id = subscription.id
            status = subscription.status
            
            return {
                "customer_id": customer_id,
                "subscription_id": subscription_id,
                "status": status,
                "event": "subscription.updated"
            }
            
        except Exception as e:
            print(f"Error handling subscription updated: {e}")
            raise

    async def handle_subscription_deleted(
        self,
        subscription: stripe.Subscription
    ) -> Dict[str, Any]:
        try:
            customer_id = subscription.customer
            subscription_id = subscription.id
            
            return {
                "customer_id": customer_id,
                "subscription_id": subscription_id,
                "event": "subscription.deleted"
            }
            
        except Exception as e:
            print(f"Error handling subscription deleted: {e}")
            raise


stripe_service = StripeService()
