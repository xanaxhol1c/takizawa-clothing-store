from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'city', 'address', 'postal_code']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None) 
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if not self.instance.pk:  
            return super().save(commit)
        return self.instance

