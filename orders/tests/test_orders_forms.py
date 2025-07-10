from decimal import Decimal
from django.test import TestCase
from main.models import Product, Category
from orders.models import Order, OrderItem
from orders.forms import OrderCreateForm

class OrderModelsTestCase(TestCase):
    def test_order_form_save(self):
        data = {
            'first_name' : 'Name',
            'last_name' : 'Surname',
            'email' : 'testmail@example.com',
            'phone_number' : '380501234567',
            'address' : '42 Tested str.',
            'postal_code' : '12345',
            'city' : 'Kyiv'
        }
        
        form = OrderCreateForm(data=data)

        self.assertTrue(form.is_valid())

        order = form.save()

        self.assertIsInstance(order, Order)
        self.assertEqual(order.first_name, 'Name')

    from django.test import TestCase
from orders.forms import OrderCreateForm
from orders.models import Order

class OrderCreateFormTestCase(TestCase):
    def test_save_on_existing_order_instance(self):
        order = Order.objects.create(
            first_name='Name',
            last_name='Surname',
            email='name1@example.com',
            phone_number='+380501234567',
            city='Kyiv',
            address='Test 42 str.',
            postal_code='12345',
        )

        form = OrderCreateForm(
            data={
                'first_name': 'Name2',
                'last_name': 'Surname2',
                'email': 'name2@example.com',
                'phone_number': '+380501234567',
                'city': 'Lviv',
                'address': 'Test 42 str.',
                'postal_code': '12345',
            },
            instance=order
        )

        self.assertTrue(form.is_valid())

        saved_order = form.save()

        self.assertEqual(saved_order.pk, order.pk)
        self.assertEqual(saved_order.email, 'name2@example.com')
