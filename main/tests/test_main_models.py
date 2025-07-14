from django.test import TestCase
from main.models import Category, Product, ProductImage
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
        
        self.product_image = ProductImage.objects.create(product=self.product, image=f'test_image_1.jpg')

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

    def test_models_str(self):
        self.assertEqual(str(self.category), self.category.name)
        self.assertEqual(str(self.product), self.product.name)
        self.assertEqual(str(self.product_image), f'{self.product.name} - {self.product_image.image}')
    
    def test_product_sell_price(self):
        self.assertEqual(self.product.sell_price(), self.product.price)

        self.product.discount = Decimal(10.00)

        self.assertEqual(self.product.sell_price(), round(self.product.price - ((self.product.price * self.product.discount) / 100), 2))