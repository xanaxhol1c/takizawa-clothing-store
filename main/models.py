from django.db import models
from django.urls import reverse

from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('main:get_products_list', args=[self.slug])

    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    image = CloudinaryField('image')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    avaliable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields = ['id', 'slug']),
                   models.Index(fields = ['name']),
                   models.Index(fields = ['-created'])
                   ]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('main:product_details', args=[self.slug])
    
    def sell_price(self):
        if self.discount:
            return round(self.price - ((self.price * self.discount) / 100), 2)
        
        return self.price

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)

    image = CloudinaryField('image')

    def __str__(self):
        return f'{self.product.name} - {self.image}'

