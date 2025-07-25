from django.shortcuts import render, redirect
from django.urls import reverse
from cart.cart import Cart
from .forms import OrderCreateForm 
from .models import OrderItem
import requests
from django.http import HttpResponse
from django.template.loader import render_to_string
from takizawa.settings import NOVA_POST_API_KEY

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

            # print(request.session['order'])
            request.session.modified = True
            return redirect(reverse('payments:process'))
        else:
            return render(request, 'order/create.html', {'cart' : cart, 'form' : form})

    else:
        form = OrderCreateForm(request=request)
        return render(request, 'order/create.html', {'cart' : cart, 'form' : form})
    
def city_autocomplete(request):
    query = request.GET.get('city')
    
    nova_post_api_url = "https://api.novaposhta.ua/v2.0/json/"

    if not query:
        return HttpResponse('')

    body = {
        "apiKey": NOVA_POST_API_KEY,
        "modelName": "AddressGeneral",
        "calledMethod": "searchSettlements",
        "methodProperties": {
            "CityName": query,
            "Limit": 5,
            "Page": 1
        }
    }

    response = requests.post(nova_post_api_url, json=body)

    cities = response.json().get('data', [])[0].get('Addresses', [])

    context = {'cities' : cities}

    html = render_to_string('partials/city_suggestions.html', context)

    return HttpResponse(html)

def address_autocomplete(request):
    query = request.GET.get('address')
    city_ref = request.GET.get('city_ref')

    if not query or not city_ref:
        return HttpResponse('')

    url = "https://api.novaposhta.ua/v2.0/json/"
    body = {
        "apiKey": NOVA_POST_API_KEY,
        "modelName": "AddressGeneral",
        "calledMethod": "searchSettlementStreets",
        "methodProperties": {
            "StreetName": query,
            "SettlementRef": city_ref,
            "Limit": 5
        }
    }

    response = requests.post(url, json=body)

    addresses = response.json().get('data', [])[0].get('Addresses', [])

    html = render_to_string('partials/address_suggestions.html', {'addresses': addresses})
    return HttpResponse(html)
