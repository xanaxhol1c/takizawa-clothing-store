from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import stripe
import json
import logging
from orders.models import Order, OrderItem
from cart.cart import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    cart = Cart(request)
    
    # Перевірка, чи кошик не порожній
    if not cart:
        return redirect('cart:cart_detail')
    
    if request.method == 'GET':
        order_data = request.session.get('order', {})
        
        # Валідація обов'язкових полів
        required_fields = ['first_name', 'last_name', 'phone_number', 'city', 'address']
        if not all(field in order_data for field in required_fields):
            logger.error("Missing required order data in session")
            return HttpResponseBadRequest("Missing required order information")

        line_items = []
        items_for_metadata = []
        
        try:
            for item in cart:
                product = item['product']
                price = product.sell_price()
                
                if not price or price <= 0:
                    logger.error(f"Invalid price for product {product.id}")
                    return HttpResponseBadRequest("Invalid product price")
                
                line_items.append({
                    'price_data': {
                        'unit_amount': int(price * Decimal('100')),  # Конвертація в копійки
                        'currency': 'uah',
                        'product_data': {
                            'name': product.name,
                        }
                    },
                    'quantity': item['quantity']
                })
                
                items_for_metadata.append({
                    'product_id': product.id,
                    'price': str(price),
                    'quantity': item['quantity'],
                    'size': item.get('size', '')
                })

            session_data = {
                'mode': 'payment',
                'success_url': request.build_absolute_uri(
                    reverse('payments:completed') + f'?session_id={{CHECKOUT_SESSION_ID}}'
                ),
                'cancel_url': request.build_absolute_uri(reverse('payments:canceled')),
                'line_items': line_items,
                'customer_email': order_data.get('email', ''),  # Додаємо email для Stripe
                'metadata': {
                    'first_name': order_data['first_name'],
                    'last_name': order_data['last_name'],
                    'phone_number': order_data['phone_number'],
                    'city': order_data['city'],
                    'address': order_data['address'],
                    'postal_code': order_data.get('postal_code', ''),
                    'items': json.dumps(items_for_metadata)
                }
            }

            session = stripe.checkout.Session.create(**session_data)
            return redirect(session.url, code=303)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return HttpResponseServerError("Payment processing error")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return HttpResponseServerError("Internal server error")

def payment_completed(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponseBadRequest("Missing session ID")
    
    try:
        # Отримуємо сесію Stripe
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=['payment_intent']
        )
        
        # Шукаємо існуюче замовлення
        try:
            order = Order.objects.get(stripe_id=session.payment_intent)
        except Order.DoesNotExist:
            logger.error(f"Order not found for payment intent {session.payment_intent}")
            return HttpResponseBadRequest("Order not found")

        # Відправка email
        try:
            message = f"""
            Dear {order.first_name} {order.last_name},

            Thank you for your order! 🎉

            Order Details:
            - Order ID: {order.id}
            - Total Amount: ₴{order.get_total_cost()}

            Items:
            """
            
            for item in order.items.all():
                message += f"- {item.product.name} (Size: {item.size}) x {item.quantity} - ₴{item.price * item.quantity}\n"

            message += f"""
            
            Shipping to:
            {order.address}, {order.city}, {order.postal_code}

            We'll notify you once your order ships.

            Best regards,
            Takizawa Shizoku Team
            """

            send_mail(
                subject="Your Order Confirmation",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")

        return render(request, 'payments/completed.html', {'order': order})
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return HttpResponseServerError("Payment verification failed")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return HttpResponseServerError("Internal server error")

def payment_canceled(request):
    return render(request, 'payments/canceled.html')

def payment_canceled(request):
    return render(request, 'payments/canceled.html')