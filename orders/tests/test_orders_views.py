from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from main.models import Product, Category

class OrderViewsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='T-Shirt', slug="t-shirt")
        
        self.product = Product.objects.create(
            category=self.category,
            name="product1",
            slug="product1", 
            price=Decimal(1000.00),
            image='test_image.jpg', 
            description="desc"
        )

    def test_get_order(self):
        response = self.client.get(reverse('orders:order_create'))    
        
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'order/create.html')
        self.assertIsNotNone(response.context['cart'])
        self.assertIsNotNone(response.context['form'])
        
    def test_post_order_valid_form(self):
        self.client.post(reverse('cart:cart_add', args=[self.product.id]),
                                   data={'quantity' : 1,
                                         'size' : 'M'},
                                    HTTP_REFERER=reverse('cart:cart_details'))
        
        valid_data={
            'first_name': 'Name',
            'last_name': 'Surname',
            'email': 'testmail@example.com',
            'phone_number': '380501234567',
            'address': '42 Tested str.',
            'postal_code': '12345',
            'city': 'Kyiv'
        }

        response = self.client.post(reverse('orders:order_create'), data=valid_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(response['Location'], reverse('payments:process'))

        session_order = self.client.session.get('order')

        self.assertIsNotNone(session_order)
        self.assertEqual(session_order['first_name'], 'Name')
        self.assertEqual(session_order['last_name'], 'Surname')
        self.assertEqual(session_order['email'], 'testmail@example.com')
        self.assertEqual(session_order['phone_number'], '+380501234567')
        self.assertEqual(session_order['address'], '42 Tested str.')
        self.assertEqual(session_order['postal_code'], '12345')
        self.assertEqual(session_order['city'], 'Kyiv')
    
    def test_post_order_not_valid_form(self):
        self.client.post(reverse('cart:cart_add', args=[self.product.id]),
                                   data={'quantity' : 1,
                                         'size' : 'M'},
                                    HTTP_REFERER=reverse('cart:cart_details'))
        
        valid_data={
            'first_name': 'Name',
            'last_name': 'Surname',
            'email': 'notanemail',
            'phone_number': '7214124501234567',
            'address': '42 Tested str.',
            'postal_code': '12345',
            'city': 'Kyiv'
        }

        response = self.client.post(reverse('orders:order_create'), data=valid_data)

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'order/create.html')
        self.assertTrue(response.context['form'].errors)

    
class OrderAutocompleteTestCase(TestCase):

    def test_autocomplete_city(self):
        response = self.client.get(reverse('orders:city-autocomplete'), {'city': 'Київ'})

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['cities'])
        self.assertEqual(len(response.context['cities']), 5)
        self.assertEqual(response.context['cities'][0]['Present'], 'м. Київ, Київська обл.')
        self.assertEqual(response.context['cities'][0]['Ref'], 'e718a680-4b33-11e4-ab6d-005056801329')

    def test_autocomplete_city_empty_query(self):
        response = self.client.get(reverse('orders:city-autocomplete'))
        self.assertEqual(response.content.decode('utf-8'), '')

    def test_autocomplete_address_with_city(self):
        response = self.client.get(reverse('orders:address-autocomplete'), 
                                   {'address' : 'Бер',
                                    'city_ref': 'e718a680-4b33-11e4-ab6d-005056801329', })

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['addresses'])
        self.assertEqual(len(response.context['addresses']), 5)
        self.assertEqual(response.context['addresses'][0]['Present'], 'просп. Берестейський')
    
    def test_autocomplete_address_empty(self):
        response = self.client.get(reverse('orders:address-autocomplete'))
        self.assertEqual(response.content.decode('utf-8'), '')

    def test_autocomplete_address_empty_city_ref(self):
        response = self.client.get(reverse('orders:address-autocomplete'), {'address' : 'Бер'})
        self.assertEqual(response.content.decode('utf-8'), '')
