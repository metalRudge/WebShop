import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render,get_object_or_404
from .models import Product


def products(request):
    products = Product.objects.filter(availability=True)
    return render(request, 'pages/products.html', {'products': products})

def product_detail(request, sku_id):
    product = get_object_or_404(Product, sku_id=sku_id)
    return render(request, 'pages/product_detail.html', {'product': product})

def home(request):
    """Render the Phase 1 Hello World / project-start page."""
    context = {
        'phase': 'Phase 1',
        'title': 'Webshop - Hello World',
    }
    return render(request, 'pages/home.html', context)
