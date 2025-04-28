from django.contrib import admin
from .models import Product, Category, ProductImage
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'discount', 'avaliable', 'created', 'updated', 'discount']

    list_filter = ['avaliable','created','updated']
    list_editable = ['price', 'avaliable', 'discount']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]