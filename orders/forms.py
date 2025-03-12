from django import forms
from .models import Order

class OrderCreateForm(forms.Form):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'city', 'address', 'postal_code']

    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)

    def save(self, commit=True):
        order = super().save(commit=False)
        if commit:
            order.save()
        return order


