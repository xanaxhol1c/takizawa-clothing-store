from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from main.models import Category, Product
from decimal import Decimal
from unittest.mock import patch, MagicMock

class IndexViewTestCase(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index/index.html')

class ProductListTestCase(TestCase):
    @patch('main.models.Product.image') 
    def setUp(self, mock_image):
        mock_image.return_value = MagicMock(url='https://fake.url/test.jpg')
        
        self.category1 = Category.objects.create(name='Pants', slug="pants")
        self.category2 = Category.objects.create(name='T-Shirt', slug="t-shirt")
        
        self.product1 = Product.objects.create(
            category=self.category1,
            name="product1",
            slug="product1", 
            price=Decimal(1000.00),
            image='test_image.jpg', 
            description="desc"
        )
        
        self.product2 = Product.objects.create(
            category=self.category2,
            name="product2",
            slug="product2", 
            price=Decimal(1500.00),
            image='test_image.jpg',  
            description="desc2"
        )

    @patch('cloudinary.uploader.upload')
    def test_all_product_list(self, mock_upload):
        mock_upload.return_value = {'secure_url': 'https://fake.url/test.jpg'}
        
        response = self.client.get(reverse('main:shop'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/product/list.html')
        self.assertEqual(None, response.context['category'])
        self.assertIn(self.category1, response.context['categories'])
        self.assertIn(self.product1, response.context['current_page'])
        self.assertEqual(1, response.context['current_page'].number)
        self.assertEqual(None, response.context['slug_url'])

    def test_product_list_with_category(self):
        response = self.client.get(reverse('main:get_products_list', args=[self.category2.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/product/list.html')
        self.assertEqual(self.category2, response.context['category'])
        self.assertIn(self.category1, response.context['categories'])
        self.assertIn(self.category2, response.context['categories'])
        self.assertNotIn(self.product1, response.context['current_page'])
        self.assertIn(self.product2, response.context['current_page'])
        self.assertEqual(1, response.context['current_page'].number)
        self.assertEqual(self.category2.slug, response.context['slug_url'])

    @patch('main.models.Product.image')
    def test_product_list_pagination(self, mock_image):
        mock_image.return_value = MagicMock(url='https://fake.url/test.jpg')
        
        for i in range(9):
            Product.objects.create(
                category=self.category1,
                name=f"Product {i}",
                slug=f"product-{i}",
                price=Decimal("1000.00"),
                image=f'test_image_{i}.jpg',
                description="Test description"
            )

        response_page_1 = self.client.get(reverse('main:shop'), {'page': 1})
        self.assertEqual(response_page_1.status_code, 200)
        self.assertTemplateUsed(response_page_1, 'main/product/list.html')
        self.assertEqual(response_page_1.context['current_page'].number, 1)
        self.assertTrue(response_page_1.context['current_page'].has_next())
        self.assertEqual(None, response_page_1.context['slug_url'])
        self.assertEqual(8, len(response_page_1.context['current_page'].object_list))

        response_page_2 = self.client.get(reverse('main:shop'), {'page': 2})
        self.assertEqual(response_page_2.status_code, 200)
        self.assertTemplateUsed(response_page_2, 'main/product/list.html')
        self.assertEqual(response_page_2.context['current_page'].number, 2)
        self.assertTrue(response_page_2.context['current_page'].has_previous())
        self.assertEqual(None, response_page_2.context['slug_url'])
        self.assertEqual(3, len(response_page_2.context['current_page'].object_list)) 

class ProductDetailsTestCase(TestCase):
    @patch('main.models.Product.image')
    def setUp(self, mock_image):
        mock_image.return_value = MagicMock(url='https://fake.url/test.jpg')
        self.category1 = Category.objects.create(name='Pants', slug="pants")
        self.product1 = Product.objects.create(
            category=self.category1,
            name="product1",
            slug="product1", 
            price=Decimal(1000.00),
            image='test_image.jpg',
            description="desc"
        )

    def test_product_details_page(self):
        response = self.client.get(reverse('main:product_details', args=[self.product1.slug]))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'main/product/details.html')
        self.assertEqual(self.product1, response.context['product'])

    def test_not_found_product_details_page(self):
        response = self.client.get(reverse('main:product_details', args=["product2"]))
        self.assertEqual(404, response.status_code)
        self.assertTemplateUsed(response, '404.html')