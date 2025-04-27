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
        # Отримуємо дані форми з сесії (якщо вони там є)
        order_data = request.session.get('order', {})
        
        # Готуємо товари для metadata
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

        session_data = {
            'mode': 'payment',
            'success_url': request.build_absolute_uri(reverse('payments:completed')),
            'cancel_url': request.build_absolute_uri(reverse('payments:canceled')),
            'line_items': line_items,
            'metadata': {
                'first_name': order_data.get('first_name', ''),
                'last_name': order_data.get('last_name', ''),
                'phone_number': order_data.get('phone_number', ''),
                'city': order_data.get('city', ''),
                'address': order_data.get('address', ''),
                'postal_code': order_data.get('postal_code', ''),
                'items': json.dumps(items_for_metadata)  # Зберігаємо товари у вигляді JSON
            }
        }

        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

    
def payment_completed(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    message = f"""
    Dear {order.first_name} {order.last_name},

    We are pleased to inform you that your payment has been successfully processed! 🎉  

    Here are the details of your order:  
    - Order ID: {order.id}  
    - Name: {order.first_name} {order.last_name}  
    - Email: {order.email}  
    - Phone: {order.phone_number}  
    - Shipping Address: {order.address}, {order.city}, {order.postal_code}  

    Ordered items:
    """

    for item in order.items.all():
        message += f"- {item.product.name} (Size: {item.size}) - {item.quantity} pcs - ₴{item.price * item.quantity}\n"

    message += f"""

    Total Amount: ₴{order.get_total_cost()}  

    Your order is now being processed, and we will update you once it has been shipped.  

    Thank you for choosing Takizawa Shizoku!  

    Best regards,  
    Takizawa Shizoku Team  
    """

    title = "Order Confirmation - Takizawa Shizoku"
    customer_email = order.email

    send_mail(title, message, settings.EMAIL_HOST_USER, [customer_email], fail_silently=True)

    return render(request, 'payments/completed.html', {'order' : order})

def payment_canceled(request):
    return render(request, 'payments/canceled.html')