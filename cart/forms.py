from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]

PRODUCT_SIZE_CHOICES = [('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)

    size = forms.ChoiceField(choices=PRODUCT_SIZE_CHOICES, required=True)

    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)