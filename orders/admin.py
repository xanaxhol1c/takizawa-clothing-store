from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 
                    'phone_number', 'city', 'address', 'postal_code', 
                    'created', 'updated', 'paid']
    list_filter = ['id', 'paid', 'created', 'updated']
    search_fields = ('stripe_id', 'first_name', 'last_name')
    inlines = [OrderItemInline]
