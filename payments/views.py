from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from orders.models import Order, OrderItem
from orders.forms import OrderCreateForm
from decimal import Decimal
from django.conf import settings
import stripe
import json

from django.http import HttpResponse

from cart.cart import Cart

from django.core.mail import send_mail


stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    cart = Cart(request)
    if request.method == 'GET':
        order_data = request.session.get('order', {})
        
        # Підготовка товарів
        line_items = []
        items_for_metadata = []
        
        for item in cart:
            price = item['product'].sell_price()
            line_items.append({
                'price_data': {
                    'unit_amount': int(price * Decimal(100)),
                    'currency': 'uah',
                    'product_data': {
                        'name': item['product'].name,
                    }
                },
                'quantity': item['quantity']
            })
            
            items_for_metadata.append({
                'product_id': item['product'].id,
                'price': str(price),
                'quantity': item['quantity'],
                'size': item.get('size', '')
            })

        # Створення сесії оплати
        session = stripe.checkout.Session.create(
            mode='payment',
            line_items=line_items,
            metadata={
                'first_name': order_data.get('first_name', ''),
                'last_name': order_data.get('last_name', ''),
                'phone_number': order_data.get('phone_number', ''),
                'city': order_data.get('city', ''),
                'address': order_data.get('address', ''),
                'postal_code': order_data.get('postal_code', ''),
                'items': json.dumps(items_for_metadata)
            },
            success_url=f"{request.build_absolute_uri(reverse('payments:completed'))}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=request.build_absolute_uri(reverse('payments:canceled'))
        )
        cart.clear()
        return redirect(session.url, code=303)

    
def payment_completed(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponse("Missing session ID", status=400)
    
    try:
        # Отримання сесії з Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Пошук замовлення по payment_intent
        order = Order.objects.get(stripe_id=session.payment_intent)

        # Відправка листа
        message = f"""..."""  # Ваш текст листа
        send_mail(
            "Order Confirmation",
            message,
            settings.EMAIL_HOST_USER,
            [order.email],
            fail_silently=True
        )
        
        return render(request, 'payments/completed.html', {'order': order})
    
    except stripe.error.StripeError as e:
        return HttpResponse("Payment verification failed", status=400)
    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    except Exception as e:
        return HttpResponse("Internal server error", status=500)
    
def payment_canceled(request):
    return render(request, 'payments/canceled.html')