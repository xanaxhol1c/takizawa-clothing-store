import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from main.models import Product
from .cart import Cart
from .forms import CartAddProductForm

from django.conf import settings
# Create your views here.

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 size=cd['size'],
                 override_quantity=cd['override'])

    if request.htmx:
        response = HttpResponse(status=204)
        response["HX-Trigger"] = json.dumps({
            "cartUpdated" : {"count" : len(cart)}
        })
        return response
    # print(request.session.get(settings.CART_SESSION_ID))

    referer = request.META.get('HTTP_REFERER')  
    return redirect(referer)


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
        
    product = get_object_or_404(Product, id=product_id)

    size = request.POST.get('size')

    cart.remove(product, size)

    return redirect('cart:cart_details')

def cart_details(request):
    cart = Cart(request)
    return render(request, 'cart/details.html', {'cart' : cart})