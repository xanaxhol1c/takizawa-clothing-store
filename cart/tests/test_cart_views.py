from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.test import TestCase
from cart.cart import Cart
from main.models import Category, Product


class CartViewsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pants', slug="pants")
        self.product1 = Product.objects.create(
            category=self.category,
            name="product1",
            slug="product1", 
            price=Decimal(1000.00),
            image='test_image.jpg', 
            description="desc"
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name="product2",
            slug="product2", 
            price=Decimal(1500.00),
            image='test_image.jpg', 
            description="desc"
        )


    def test_cart_details_page(self):
        response = self.client.get(reverse('cart:cart_details'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'cart/details.html')


    def test_correct_add_view(self):
        url = reverse('cart:cart_add', args=[self.product1.id])
        referer = reverse('cart:cart_details')
        
        response = self.client.post(url, data={
            'quantity' : 1,
            'size': 'M'
        }, 
        HTTP_REFERER=referer)


        self.assertEqual(response.status_code, 302)
        self.assertIn('cart', self.client.session)
        self.assertIn(f"{self.product1.id}_M", self.client.session['cart'])

        cart_item = self.client.session['cart'][f"{self.product1.id}_M"]

        self.assertEqual(cart_item['quantity'], 1)
        self.assertEqual(cart_item['size'], 'M')
        self.assertEqual(cart_item['price'], '1000.00')

    def test_add_view_override_quantity(self):
        self.client.post(
            reverse('cart:cart_add', args=[self.product1.id]),
            data={
                'quantity': 1,
                'size': 'L',
                'override': False
            },
            HTTP_REFERER=reverse('cart:cart_details')
        )

        self.client.post(
            reverse('cart:cart_add', args=[self.product1.id]),
            data={
                'quantity': 5,
                'size': 'L',
                'override': True
            },
            HTTP_REFERER=reverse('cart:cart_details')
        )

        cart = self.client.session['cart']
        self.assertEqual(cart[f"{self.product1.id}_L"]['quantity'], 5)


    def test_incorrect_add_view(self):
        url = reverse('cart:cart_add', args=[self.product1.id])
        referer = reverse('cart:cart_details')
        
        response = self.client.post(url, data={
            'quantity' : 'abc',
            'size': 123
        }, 
        HTTP_REFERER=referer)


        self.assertEqual(response.status_code, 302)
        self.assertIn('cart', self.client.session)
        self.assertNotIn(f"{self.product1.id}_M", self.client.session['cart'])

    def test_cart_total_price(self):
        add_url = reverse('cart:cart_add', args=[self.product1.id])
        referer = reverse('cart:cart_details')
        self.client.post(add_url, data={
            'quantity' : 2,
            'size' : 'M'
        },
        HTTP_REFERER=referer)
        add_url = reverse('cart:cart_add', args=[self.product2.id])
        response = self.client.post(add_url, data={
            'quantity' : 2,
            'size' : 'M'
        },
        HTTP_REFERER=referer)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('cart', self.client.session)
        self.assertIn(f"{self.product1.id}_M", self.client.session['cart'])
        self.assertIn(f"{self.product2.id}_M", self.client.session['cart'])

        request = self.client.get(reverse('cart:cart_details')).wsgi_request    

        cart = Cart(request)

        self.assertEqual('5000.00', cart.total_price())

    def test_cart_remove_directly(self):
        add_url = reverse('cart:cart_add', args=[self.product1.id])
        referer = reverse('cart:cart_details')
        self.client.post(add_url, data={
            'quantity' : 2,
            'size' : 'M'
        },
        HTTP_REFERER=referer)

        request = self.client.get(reverse('cart:cart_details')).wsgi_request    

        cart = Cart(request)

        key = f"{self.product1.id}_M"

        self.assertIn(key, cart.cart)

        cart.remove(self.product1, size='M')

        self.assertNotIn(key, cart.cart)

    def test_cart_clear_directly(self):
        add_url = reverse('cart:cart_add', args=[self.product1.id])
        referer = reverse('cart:cart_details')
        self.client.post(add_url, data={
            'quantity' : 1,
            'size' : 'M'
        },
        HTTP_REFERER=referer)

        request = self.client.get(reverse('cart:cart_details')).wsgi_request    

        cart = Cart(request)

        self.assertIn(settings.CART_SESSION_ID, request.session)

        cart.clear()

        self.assertNotIn(settings.CART_SESSION_ID, request.session)

    def test_remove_view(self):
        add_url = reverse('cart:cart_remove', args=[self.product1.id])
        referer = reverse('cart:cart_details')
        
        self.client.post(add_url, data={
            'quantity' : 1,
            'size': 'M'
        }, 
        HTTP_REFERER=referer)

        remove_url = reverse('cart:cart_remove', args=[self.product1.id])
        
        response = self.client.post(remove_url, data={
            'size': 'M'
        }, 
        HTTP_REFERER=referer)


        self.assertEqual(response.status_code, 302)
        self.assertIn('cart', self.client.session)
        self.assertNotIn(f"{self.product1.id}_M", self.client.session['cart'])

