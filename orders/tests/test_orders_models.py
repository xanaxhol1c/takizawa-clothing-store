from decimal import Decimal
from django.test import TestCase
from main.models import Product, Category
from orders.models import Order, OrderItem

class OrderModelsTestCase(TestCase):
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

        self.order = Order.objects.create(
            first_name='Name',
            last_name='Surname',
            email='testmail@example.com',
            phone_number='380501234567',
            address='42 Tested str.',
            postal_code='12345',
            city='Kyiv'
        )

        self.item1 = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal("100.00"),
            quantity=2,
            size="M"
        )

        self.item2 = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=Decimal("50.00"),
            quantity=1,
            size="L"
        )

    def test_models_str(self):
        self.assertEqual(str(self.order), f'Order {self.order.id}')
        self.assertEqual(str(self.item1), '1')
        self.assertEqual(str(self.item2), '2')

    def test_order_get_total_cost(self):
        self.assertEqual(Decimal(250), self.order.get_total_cost())
        