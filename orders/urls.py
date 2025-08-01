from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('city-autocomplete/', views.city_autocomplete, name='city-autocomplete'),
    path('address-autocomplete/', views.address_autocomplete, name='address-autocomplete'),
]