from django.test import TestCase
from django.urls import reverse
from main.models import Category, Product
from decimal import Decimal

class IndexViewTestCase(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index/index.html')


class ProductListTestCase(TestCase):
    def test_all_product_list(self):
        category1 = Category.objects.create(name='Pants', slug="pants")
        product1 = Product.objects.create(category=category1,
                                          name="product1",
                                          slug="product1", 
                                          price=Decimal(1000.00),
                                          image="produts/2025/03/08/ultimate_muscules_pic1.png",
                                          description="desc")
        response = self.client.get(reverse('main:shop'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/product/list.html')
        self.assertEqual(None, response.context['category'])
        self.assertIn(category1, response.context['categories'])
        self.assertIn(product1, response.context['current_page'])
        self.assertEqual(1, response.context['current_page'].number)
        self.assertEqual(None, response.context['slug_url'])

    def test_product_list_with_category(self):
        category1 = Category.objects.create(name='Pants', slug="pants")
        product1 = Product.objects.create(category=category1,
                                          name="product1",
                                          slug="product1", 
                                          price=Decimal(1000.00),
                                          image="produts/2025/03/08/ultimate_muscules_pic1.png",
                                          description="desc")
        category2 = Category.objects.create(name='T-Shirt', slug="t-shirt")
        product2 = Product.objects.create(category=category2,
                                          name="product2",
                                          slug="product2", 
                                          price=Decimal(1500.00),
                                          image="produts/2025/03/08/ultimate_muscules_pic1.png",
                                          description="des2")
        
        response = self.client.get(reverse('main:get_products_list', args=[category2.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/product/list.html')
        self.assertEqual(category2, response.context['category'])
        self.assertIn(category1, response.context['categories'])
        self.assertIn(category2, response.context['categories'])
        self.assertNotIn(product1, response.context['current_page'])
        self.assertIn(product2, response.context['current_page'])
        self.assertEqual(1, response.context['current_page'].number)
        self.assertEqual(category2.slug, response.context['slug_url'])

    def test_product_list_pagiantion(self):
        category1 = Category.objects.create(name='Pants', slug="pants")
        for i in range(9):
            Product.objects.create(
                category=category1,
                name=f"Product {i}",
                slug=f"product-{i}",
                price=Decimal("1000.00"),
                image="products/sample.png",
                description="Test description"
            )

        
        response_page_1 = self.client.get(reverse('main:shop'), {'page' : 1})
        
        self.assertEqual(response_page_1.status_code, 200)
        self.assertTemplateUsed(response_page_1, 'main/product/list.html')
        self.assertEqual(response_page_1.context['current_page'].number, 1)
        self.assertTrue(response_page_1.context['current_page'].has_next())
        self.assertEqual(None, response_page_1.context['slug_url'])
        self.assertEqual(8, len(response_page_1.context['current_page'].object_list))

        response_page_2 = self.client.get(reverse('main:shop'), {'page' : 2})

        self.assertEqual(response_page_2.status_code, 200)
        self.assertTemplateUsed(response_page_2, 'main/product/list.html')
        self.assertEqual(response_page_2.context['current_page'].number, 2)
        self.assertTrue(response_page_2.context['current_page'].has_previous())
        self.assertEqual(None, response_page_2.context['slug_url'])
        self.assertEqual(1, len(response_page_2.context['current_page'].object_list))


class ProductDetailsTestCase(TestCase):
    def test_product_details_page(self):
        category1 = Category.objects.create(name='Pants', slug="pants")
        product1 = Product.objects.create(category=category1,
                                          name="product1",
                                          slug="product1", 
                                          price=Decimal(1000.00),
                                          image="produts/2025/03/08/ultimate_muscules_pic1.png",
                                          description="desc")

        response = self.client.get(reverse('main:product_details', args=[product1.slug]))

        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'main/product/details.html')
        self.assertEqual(product1, response.context['product'])

    def test_not_found_product_details_page(self):
        category1 = Category.objects.create(name='Pants', slug="pants")
        product1 = Product.objects.create(category=category1,
                                          name="product1",
                                          slug="product1", 
                                          price=Decimal(1000.00),
                                          image="produts/2025/03/08/ultimate_muscules_pic1.png",
                                          description="desc")

        response = self.client.get(reverse('main:product_details', args=["product2"]))

        self.assertEqual(404, response.status_code)
        self.assertTemplateUsed(response, '404.html')
