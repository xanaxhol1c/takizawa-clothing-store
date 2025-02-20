from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def index(request):
    return render(request, 'main/index/index.html')

def get_popular_list(request):
    products = Product.objects.filter(avaliable=True)[:3]
    return render(request, 'main/index/index.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, avaliable=True)
    return render(request, 'main/product/details.html', {'product': product})