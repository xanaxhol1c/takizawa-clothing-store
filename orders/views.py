from django.shortcuts import render
from cart.cart import Cart
from .forms import OrderCreateForm 
from .models import OrderItem


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request=request)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear()
            return render(request, 'order/created.html', {'order' : order, 'form' : form})
        else:
            return render(request, 'order/create.html', {'cart' : cart, 'form' : form})

    else:
        form = OrderCreateForm(request=request)
        return render(request, 'order/create.html', {'cart' : cart, 'form' : form})
