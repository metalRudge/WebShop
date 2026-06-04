from .models import Product, Category
from django.http import HttpResponse
from django.urls import reverse 
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.db import models
from .cart import get_cart_meta, add_to_cart, remove_from_cart
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def cart(request):
    if request.method == "POST":
        action = request.POST.get("action")
        sku_id = request.POST.get("sku")

        if action == "increase":
            # sku_id is a string; get the Product instance
            product = get_object_or_404(Product, sku_id=sku_id)
            add_to_cart(request, product)
        elif action == "decrease":
            # use your decrease_quantity helper instead of a flag
            from .cart import decrease_quantity
            decrease_quantity(request, sku_id)
        elif action == "remove":
            remove_from_cart(request, sku_id)

        context = _build_cart_context(request)
        # Just return the partial; no HX-Trigger needed anymore
        return render(request, "partials/cart_content.html", context)

    # Plain GET → full page
    return render(request, "pages/cart.html", _build_cart_context(request))


def _build_cart_context(request) -> dict:
    cart: dict = request.session.get("cart", {})
    products = Product.objects.filter(sku_id__in=cart.keys())
    product_map = {p.sku_id: p for p in products}

    cart_items = []
    for sku, item in cart.items():
        p = product_map.get(sku)
        if not p:
            continue

        quantity = item.get("quantity", 0)
        subtotal = p.price * quantity
        cart_items.append(
            {
                "sku": sku,
                "product_name": p.product_name,
                "price": p.price,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    cart_total = sum(i["subtotal"] for i in cart_items)

    context = {
        "cart_items": cart_items,
        "cart_total": cart_total,
    }
    context.update(get_cart_meta(request))  # adds meta.cart_count
    return context


def products(request):
    category = request.GET.get("category")
    qs = Product.objects.filter(availability=True)

    if category:
        qs = qs.filter(categories__name=category)

    categories = Category.objects.all().order_by("name")

    return render(request, "pages/products.html", {
        "products": qs,
        "categories": categories,
        "active_category": category,
    })


@require_http_methods(["GET", "POST"])
def product_detail(request, sku_id):
    product = get_object_or_404(Product, sku_id=sku_id)

    if request.method == "POST" and request.POST.get("action") == "add_to_cart":
        try:
            add_to_cart(request, product)
            count = get_cart_meta(request)["meta"]["cart_count"]
            html = (
                '✓ Added to cart'
                f'<span id="cart-badge" hx-swap-oob="true" '
                'class="inline-flex items-center justify-center rounded-full '
                'bg-indigo-600 px-1.5 py-0.5 text-xs font-semibold text-white '
                f'min-w-[1.25rem]{" hidden" if not count else ""}">'
                f'{count}</span>')
            return HttpResponse(html)
        except Exception as e:
            logger.error(f"Failed to add {sku_id} to cart: {e}")
            return HttpResponse('Failed to add item.', status=500)

    return render(request, "pages/product_detail.html", {"product": product})

def checkout(request):
    context = _build_cart_context(request)
    return render(request, "pages/checkout.html",context)

def about(request):
    return render(request,"pages/about.html")

def search(request):
    query = request.GET.get("q","").strip()
    results = Product.objects.none()

    if query:
        results = Product.objects.filter(availability=True).filter(models.Q(product_name__icontains=query) | models.Q(sku_id__icontains=query) | models.Q(categories__icontains=query))
    return render(request,"pages/search.html",{
        "results":results,
        "query":query,
    })