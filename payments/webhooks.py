import stripe
import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order, OrderItem
from orders.forms import OrderCreateForm
from decimal import Decimal


logger = logging.getLogger(__name__)

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
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                # Перевіряємо, чи замовлення вже існує
                if Order.objects.filter(stripe_id=session.payment_intent).exists():
                    logger.info(f"Order already exists for payment intent {session.payment_intent}")
                    return HttpResponse(status=200)
                
                metadata = session.metadata
                
                order = Order.objects.create(
                    first_name=metadata.get('first_name', ''),
                    last_name=metadata.get('last_name', ''),
                    email=session.customer_details.email if session.customer_details else '',
                    phone_number=metadata.get('phone_number', ''),
                    city=metadata.get('city', ''),
                    address=metadata.get('address', ''),
                    postal_code=metadata.get('postal_code', ''),
                    paid=True,
                    stripe_id=session.payment_intent  # Тепер це поле існує
                )

                try:
                    items = json.loads(metadata.get('items', '[]'))
                    for item in items:
                        OrderItem.objects.create(
                            order=order,
                            product_id=item['product_id'],
                            price=Decimal(item['price']),
                            quantity=item['quantity'],
                            size=item.get('size', '')
                        )
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error parsing order items: {str(e)}")
                    order.delete()
                    return HttpResponse(status=400)

                logger.info(f"Successfully created order {order.id}")
                
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}")
                return HttpResponse(status=500)

    return HttpResponse(status=200)