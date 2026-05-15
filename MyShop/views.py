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
@require_POST
def cart_add(request, sku_id):
    product = get_object_or_404(Product, sku_id=sku_id)
    try:
        meta = add_to_cart(request, product)
        return JsonResponse({
            'cart_count': meta['cart_count'],
            'cart_total': float(meta['cart_total']),
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except RuntimeError:
        return JsonResponse({'error': 'Failed to add item to cart.'}, status=500)


@require_POST
def cart_remove(request, sku_id):
    try:
        meta = remove_from_cart(request, sku_id)
        return JsonResponse({
            'cart_count': meta['cart_count'],
            'cart_total': float(meta['cart_total']),
        })
    except RuntimeError:
        return JsonResponse({'error': 'Failed to remove item from cart.'}, status=500)


@require_POST
def cart_update(request, sku_id):
    try:
        quantity = int(request.POST.get('quantity', 1))
        meta = update_cart_quantity(request, sku_id, quantity)
        return JsonResponse({
            'cart_count': meta['cart_count'],
            'cart_total': float(meta['cart_total']),
        })
    except (ValueError, RuntimeError):
        return JsonResponse({'error': 'Failed to update cart.'}, status=500)


def cart_detail(request):
    cart = get_cart(request)
    meta = get_cart_meta(request)
    items = {k: v for k, v in cart.items() if k != '_meta'}
    return render(request, 'cart.html', {
        'items': items,
        'meta': meta,
    })

def home(request):
    """Render the Phase 1 Hello World / project-start page."""
    context = {
        'phase': 'Phase 1',
        'title': 'Webshop - Hello World',
    }
    return render(request, 'pages/home.html', context)
