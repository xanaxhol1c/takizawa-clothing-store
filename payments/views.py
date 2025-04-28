from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from orders.models import Order, OrderItem
from orders.forms import OrderCreateForm
from decimal import Decimal
from django.conf import settings
import stripe

from django.http import HttpResponse

from cart.cart import Cart

from django.core.mail import send_mail


stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    cart = Cart(request)
    if request.method == 'GET':
        success_url = request.build_absolute_uri(reverse('payments:completed'))

        cancel_url = request.build_absolute_uri(reverse('payments:canceled'))

        session_data = {
            'mode': 'payment',
            # 'client_reference_id': order.id,
            'success_url' : success_url,
            'cancel_url' : cancel_url,
            'line_items': []
        }
        for item in cart:
            price = item['product'].sell_price()
            session_data['line_items'].append({ 
                'price_data': {
                    'unit_amount': int(price * Decimal(100)),
                    'currency': 'uah',
                    'product_data': {
                        'name': item['product'].name,
                    }
                },
                'quantity': item['quantity']
            })
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

    
def payment_completed(request):
    cart = Cart(request)

    form_data = {
        'first_name': request.session['order']['first_name'],
        'last_name': request.session['order']['last_name'],
        'email': request.session['order']['email'],
        'phone_number': request.session['order']['phone_number'],
        'city': request.session['order']['city'],
        'address': request.session['order']['address'],
        'postal_code': request.session['order']['postal_code'],
    }

    form = OrderCreateForm(form_data)

    if form.is_valid():
        order = form.save(commit=False)
        order.paid = True  
        order.stripe_id = request.session.get('order_stripe_id')
        order.save()

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity'],
                size = item['size']
            )
        
        cart.clear()

        request.session['order_id'] = order.id
        request.session.modified = True

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