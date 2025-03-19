from django.shortcuts import render, redirect
from django.urls import reverse
from cart.cart import Cart
from .forms import OrderCreateForm 
from .models import OrderItem

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request=request)
        if form.is_valid():
            order = form.cleaned_data

            request.session['order'] = {
                'first_name': str(order['first_name']),
                'last_name': str(order['last_name']),
                'email': str(order['email']),
                'phone_number': str(order['phone_number']),
                'address': str(order['address']),
                'postal_code': str(order['postal_code']),
                'city': str(order['city'])
            }

            print(request.session['order'])
            request.session.modified = True
            return redirect(reverse('payments:process'))
        else:
            return render(request, 'order/create.html', {'cart' : cart, 'form' : form})

    else:
        form = OrderCreateForm(request=request)
        return render(request, 'order/create.html', {'cart' : cart, 'form' : form})
