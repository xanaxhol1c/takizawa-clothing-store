from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
from django.conf import settings
from decimal import Decimal

from orders.models import Order, OrderItem
import json


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                metadata = session.metadata
                
                # Створення замовлення
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

                # Додавання товарів
                items = json.loads(metadata.get('items', '[]'))
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item['product_id'],
                        price=item['price'],
                        quantity=item['quantity'],
                        size=item.get('size', '')
                    )

            except Exception as e:
                return HttpResponse(status=500)

    return HttpResponse(status=200)