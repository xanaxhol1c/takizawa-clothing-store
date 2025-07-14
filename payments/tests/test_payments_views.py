from decimal import Decimal
from unittest.mock import patch
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from main.models import Product, Category
from orders.models import Order

class PaymentsViewsTestCase(TestCase):
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
        
        add_url = reverse('cart:cart_add', args=[self.product1.id])
        self.client.post(add_url, data={
            'quantity' : 2,
            'size' : 'M'
        },
        HTTP_REFERER=reverse('cart:cart_details'))

        valid_data = {
            'first_name' : 'Name',
            'last_name' : 'Surname',
            'email' : 'testmail@example.com',
            'phone_number' : '380501234567',
            'address' : '42 Tested str.',
            'postal_code' : '12345',
            'city' : 'Kyiv'
        }

        self.session = self.client.session
        self.session['order'] = valid_data
        self.session.save()

    @patch('payments.views.stripe.checkout.Session.create')
    def test_payment_process_view(self, mock_create):
        mock_create.return_value.url = 'https://fake.stripe/checkout'

        response = self.client.get(reverse('payments:process'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://fake.stripe/checkout')

        mock_create.assert_called_once()
        data_passed = mock_create.call_args[1]
        self.assertIn('line_items', data_passed)
        self.assertEqual(data_passed['mode'], 'payment')

    def test_payment_completed_valid_view(self):
        response = self.client.get(reverse('payments:completed'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/completed.html')

        orders = Order.objects.all()

        self.assertEqual(len(orders), 1)

        order = orders.first()

        self.assertEqual(order.first_name, 'Name')
        self.assertEqual(order.last_name, 'Surname')
        self.assertEqual(order.email, 'testmail@example.com')
        self.assertEqual(order.phone_number, '+380501234567')
        self.assertEqual(order.address, '42 Tested str.')
        self.assertEqual(order.postal_code, '12345')
        self.assertEqual(order.city, 'Kyiv')

        self.assertEqual(order.paid, True)

        items = order.items.all()

        self.assertEqual(items.count(), 1)
        self.assertEqual(items.first().product, self.product1)
        self.assertEqual(items.first().quantity, 2)

        self.assertEqual(self.client.session['cart'], dict())

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Order Confirmation", mail.outbox[0].subject)

    def test_payment_completed_invalid_view(self):
        invalid_data={
            'first_name': 'Name',
            'last_name': 'Surname',
            'email': 'notanemail',
            'phone_number': '7214124501234567',
            'address': '42 Tested str.',
            'postal_code': '12345',
            'city': 'Kyiv'
        }

        self.session = self.client.session
        self.session['order'] = invalid_data
        self.session.save()

        response = self.client.get(reverse('payments:completed'))
        
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_payment_cancelled_view(self):
        response = self.client.get(reverse('payments:canceled'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/canceled.html')
