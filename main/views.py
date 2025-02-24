from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category

def index(request):
    return render(request, 'main/index/index.html')

def get_products_list(request, category_slug = None):
    page = request.GET.get('page', 1)
    category = None
    categories = Category.objects.all().order_by('id')
    products = Product.objects.filter(avaliable=True).order_by('category_id')

    if category_slug:
        category = get_object_or_404(Category, slug = category_slug)
        products = Product.objects.filter(category=category)
        paginator = Paginator(products, 8)
        current_page = paginator.page(int(page))
    else:
        paginator = Paginator(products, 8)
        current_page = paginator.page(int(page))

    return render(request, 'main/product/list.html', {'category': category, 'categories': categories, 'current_page': current_page, 'slug_url' : category_slug})

# def categories_list(request):
#     categories = Category.objects.all().order_by('id')


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, avaliable=True)
    return render(request, 'main/product/details.html', {'product': product})