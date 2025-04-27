import stripe
import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order, OrderItem
from orders.forms import OrderCreateForm

logger = logging.getLogger(__name__)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                metadata = session.metadata
                
                # Створюємо замовлення ТІЛЬКИ при успішній оплаті
                order = Order.objects.create(
                    first_name=metadata.get('first_name', ''),
                    last_name=metadata.get('last_name', ''),
                    email=session.customer_details.email if session.customer_details else '',
                    phone_number=metadata.get('phone_number', ''),
                    city=metadata.get('city', ''),
                    address=metadata.get('address', ''),
                    postal_code=metadata.get('postal_code', ''),
                    paid=True,
                    stripe_id=session.payment_intent
                )

                # Додаємо товари
                items = json.loads(metadata.get('items', '[]'))
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item['product_id'],
                        price=item['price'],
                        quantity=item['quantity'],
                        size=item.get('size', '')
                    )
                
                logger.info(f"Order {order.id} created successfully")

            except Exception as e:
                logger.error(f"Error processing order: {e}")
                return HttpResponse(status=500)

    return HttpResponse(status=200)