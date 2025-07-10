from django.test import TestCase
from main.models import Category, Product
from decimal import Decimal

class ModelsTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Shirts", slug="shirts")

        self.product = Product.objects.create(
            category=self.category,
            name=f"Test Shirt",
            slug=f"test-shirt",
            price=Decimal("1000.00"),
            image=f'test_image_1.jpg',
            description="Test description"
        )

    def test_create_category(self):
        self.assertEqual('Shirts', self.category.name)
        self.assertEqual('shirts', self.category.slug)
        self.assertEqual('/shop/category/shirts/', self.category.get_absolute_url())

    
    def test_create_product(self):
        self.assertEqual(self.product.name, "Test Shirt")
        self.assertEqual(str(self.product), "Test Shirt")
        self.assertEqual(self.category, self.product.category)
    
    def test_get_absolute_url(self):
        self.assertEqual('/shop/test-shirt/', self.product.get_absolute_url())