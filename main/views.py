from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def index(request):
    return render(request, 'main/index/index.html')

def get_all_list(request):
    categories = Category.objects.all().order_by('id')
    products_by_categories = {category: Product.objects.filter(avaliable=True, category=category) for category in categories}

    return render(request, 'main/product/list.html', {'products_by_categories': products_by_categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, avaliable=True)
    return render(request, 'main/product/details.html', {'product': product})