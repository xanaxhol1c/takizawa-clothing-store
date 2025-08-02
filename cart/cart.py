from decimal import Decimal
from django.conf import settings
from main.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, size='None', override_quantity = False):
        product_key = f"{product.id}_{size}"

        if product_key not in self.cart:
            self.cart[product_key] = {'quantity': 0, 'size': size, 'price': str(product.price)}

        if override_quantity:
            self.cart[product_key]['quantity'] = quantity
        else:
            self.cart[product_key]['quantity'] += quantity
        self.save()

    def remove(self, product, size):
        product_key = f"{product.id}_{size}"
        if product_key in self.cart:
            del self.cart[product_key]
            self.save()

    def save(self):
        self.session.modified = True

    def total_price(self):
        total_price = Decimal("0.0")
        
        for item in self:
            total_price += Decimal(item['total_price'])
        return format(total_price, '.2f')
    
    def __iter__(self):
        product_keys = self.cart.keys()
        product_ids = {key.split('_')[0] for key in product_keys} 
        products = Product.objects.filter(id__in=product_ids)
        products_dict = {str(product.id): product for product in products}

        for product_key, item in self.cart.items():
            product_id, size = product_key.split('_')
            product = products_dict.get(product_id)

            if product:
                item_copy = item.copy()
                item_copy['product'] = product
                item_copy['size'] = size  

                price = Decimal(item['price']) - (Decimal(item['price']) * Decimal(product.discount)) / 100
                item_copy['price'] = format(price, '.2f')
                item_copy['total_price'] = format(price * item['quantity'], '.2f')

            yield item_copy


    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
        
