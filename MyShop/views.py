from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from .models import Product
from .cart import get_cart_meta, add_to_cart, remove_from_cart
import logging

logger = logging.getLogger(__name__)

def products(request):
    products = Product.objects.filter(availability=True)
    return render(request, 'pages/products.html', {'products': products})

@require_http_methods(["GET", "POST"])
def product_detail(request, sku_id):
    product = get_object_or_404(Product, sku_id=sku_id)

    if request.method == "POST" and request.POST.get("action") == "add_to_cart":
        try:
            add_to_cart(request, product.sku_id)
            response = HttpResponse('<span class="text-green-600 font-medium">✓ Added to cart</span>')
            response["HX-Trigger"] = "cartUpdated"
            return response
        except Exception as e:
            logger.error(f"Failed to add {sku_id} to cart: {e}")
            return HttpResponse('<span class="text-red-600 font-medium">Failed to add item.</span>', status=500)

    return render(request, "pages/product_detail.html", {"product": product})



@require_http_methods(["GET", "POST"])
def cart(request):
    if request.method == "POST":
        action = request.POST.get("action")
        sku_id = request.POST.get("sku")

        if action == "increase":
            add_to_cart(request, sku_id)
        elif action == "decrease":
            remove_from_cart(request, sku_id, decrease=True)
        elif action == "remove":
            remove_from_cart(request, sku_id)

        context  = _build_cart_context(request)
        response = render(request, "partials/cart_content.html", context)
        response["HX-Trigger"] = "cartUpdated"
        return response

    return render(request, "pages/cart.html", _build_cart_context(request))


def _build_cart_context(request) -> dict:
    cart: dict = request.session.get("cart", {})
    products   = Product.objects.filter(sku_id__in=cart.keys())
    product_map = {p.sku_id: p for p in products}

    cart_items = [
        {
            "sku":      sku,
            "name":     p.name,
            "price":    p.price,
            "quantity": qty,
            "subtotal": p.price * qty,
        }
        for sku, qty in cart.items()
        if (p := product_map.get(sku))
    ]

    return {
        "cart_items":  cart_items,
        "cart_total":  sum(i["subtotal"] for i in cart_items),
    }


def home(request):
    """Render the Phase 1 Hello World / project-start page."""
    context = {
        'phase': 'Phase 1',
        'title': 'Webshop - Hello World',
    }
    return render(request, 'pages/home.html', context)
