import stripe
from django.conf import settings
from django.http import HttpResponse
import stripe.error
from main.models import Product
from orders.models import Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from cart.cart import Cart
from orders.forms import OrderCreateForm


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )

    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)


    if event.type == 'checkout.session.completed':
        session = event.data.object

        if session.mode == 'payment' and session.payment_status == 'paid':
            request.session['order_stripe_id'] = session.payment_intent  # Зберігаємо ID Stripe платежу

    return HttpResponse(status=200)
