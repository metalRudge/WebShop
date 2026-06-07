import logging
import jwt
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .cart import add_to_cart, decrease_quantity, get_cart_meta, remove_from_cart
from .models import Address, Category, Order, OrderItem, Product


logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
#  JWT helpers
# ═══════════════════════════════════════════════════════════

def _generate_tokens(user):
    now = datetime.datetime.utcnow()
    access_payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": now + datetime.timedelta(minutes=30),
        "type": "access",
    }
    refresh_payload = {
        "user_id": user.id,
        "exp": now + datetime.timedelta(days=7),
        "type": "refresh",
    }
    access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")
    return access_token, refresh_token


def _set_auth_session(request, user, tokens):
    access_token, refresh_token = tokens
    request.session["access_token"] = access_token
    request.session["refresh_token"] = refresh_token
    request.session["user_id"] = user.id
    request.session["username"] = user.username


def jwt_required(view_func):
    def wrapper(request, *args, **kwargs):
        token = request.session.get("access_token")
        if not token:
            return redirect("login")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "access":
                raise jwt.InvalidTokenError
            request.user_payload = payload
        except jwt.ExpiredSignatureError:
            return redirect("token_refresh")
        except jwt.InvalidTokenError:
            request.session.flush()
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# ═══════════════════════════════════════════════════════════
#  Cart
# ═══════════════════════════════════════════════════════════

def _build_cart_context(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(sku_id__in=cart.keys())
    product_map = {p.sku_id: p for p in products}

    cart_items = []
    for sku, item in cart.items():
        product = product_map.get(sku)
        if not product:
            continue
        quantity = item.get("quantity", 0)
        cart_items.append({
            "sku": sku,
            "product_name": product.product_name,
            "price": product.price,
            "quantity": quantity,
            "subtotal": product.price * quantity,
        })

    context = {
        "cart_items": cart_items,
        "cart_total": sum(i["subtotal"] for i in cart_items),
    }
    context.update(get_cart_meta(request))
    return context


@require_http_methods(["GET", "POST"])
def cart(request):
    if request.method == "POST":
        action = request.POST.get("action")
        sku_id = request.POST.get("sku")

        if action == "increase":
            product = get_object_or_404(Product, sku_id=sku_id)
            add_to_cart(request, product)
        elif action == "decrease":
            decrease_quantity(request, sku_id)
        elif action == "remove":
            remove_from_cart(request, sku_id)

        return render(request, "partials/cart_content.html", _build_cart_context(request))

    return render(request, "pages/cart.html", _build_cart_context(request))


# ═══════════════════════════════════════════════════════════
#  Catalog
# ═══════════════════════════════════════════════════════════

def products(request):
    category = request.GET.get("category")
    qs = Product.objects.filter(availability=True)
    if category:
        qs = qs.filter(categories__name=category)

    return render(request, "pages/products.html", {
        "products": qs,
        "categories": Category.objects.all().order_by("name"),
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
                f'{count}</span>'
            )
            return HttpResponse(html)
        except Exception as e:
            logger.error(f"Failed to add {sku_id} to cart: {e}")
            return HttpResponse("Failed to add item.", status=500)

    return render(request, "pages/product_detail.html", {"product": product})


def search(request):
    query = request.GET.get("q", "").strip()
    results = Product.objects.none()

    if query:
        results = Product.objects.filter(availability=True).filter(
            models.Q(product_name__icontains=query) | models.Q(sku_id__icontains=query)
        )

    return render(request, "pages/search.html", {"results": results, "query": query})


# ═══════════════════════════════════════════════════════════
#  Auth
# ═══════════════════════════════════════════════════════════

def login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, "pages/login.html", {"error": "Invalid username or password."})

        _set_auth_session(request, user, _generate_tokens(user))
        return redirect("account")

    return render(request, "pages/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        verify_password = request.POST.get("verify_password", "").strip()

        if password != verify_password:
            return render(request, "pages/register.html", {"error": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, "pages/register.html", {"error": "Username already taken."})

        if User.objects.filter(email=email).exists():
            return render(request, "pages/register.html", {"error": "Email already registered."})

        user = User.objects.create_user(username=username, email=email, password=password)
        _set_auth_session(request, user, _generate_tokens(user))
        return redirect("account")

    return render(request, "pages/register.html")


def logout(request):
    request.session.flush()
    return redirect("home")


def token_refresh(request):
    refresh_token = request.session.get("refresh_token")
    if not refresh_token:
        return JsonResponse({"error": "No refresh token."}, status=401)

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError

        user = User.objects.get(id=payload["user_id"])
        access_token, _ = _generate_tokens(user)
        request.session["access_token"] = access_token
        return JsonResponse({"access_token": access_token})

    except jwt.ExpiredSignatureError:
        request.session.flush()
        return JsonResponse({"error": "Session expired. Please log in again."}, status=401)
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return JsonResponse({"error": "Invalid token."}, status=401)


# ═══════════════════════════════════════════════════════════
#  Account
# ═══════════════════════════════════════════════════════════

@jwt_required
def account(request):
    user = User.objects.get(id=request.session.get("user_id"))
    orders = Order.objects.filter(email=user.email).order_by("-created_at")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            user.first_name = request.POST.get("first_name", "").strip()
            user.last_name = request.POST.get("last_name", "").strip()
            user.email = request.POST.get("email", "").strip()
            user.save()
            request.session["username"] = user.username

        elif action == "add_address":
            Address.objects.create(
                user=user,
                label=request.POST.get("label", "Home").strip(),
                line1=request.POST.get("line1", "").strip(),
                line2=request.POST.get("line2", "").strip(),
                city=request.POST.get("city", "").strip(),
                state=request.POST.get("state", "").strip(),
                postal_code=request.POST.get("postal_code", "").strip(),
                country=request.POST.get("country", "Serbia").strip(),
                is_default=request.POST.get("is_default") == "on",
            )

        elif action == "delete_address":
            addr_id = request.POST.get("address_id")
            Address.objects.filter(id=addr_id, user=user).delete()

        return redirect("account")

    return render(request, "pages/account.html", {
        "user": user,
        "orders": orders,
        "addresses": user.addresses.all(),
        "default_address": user.addresses.filter(is_default=True).first(),
    })


# ═══════════════════════════════════════════════════════════
#  Checkout & Orders
# ═══════════════════════════════════════════════════════════

def checkout(request):
    if request.method == "POST":
        context = _build_cart_context(request)
        cart_items = context["cart_items"]
        cart_total = context["cart_total"]

        if not cart_items:
            return redirect("cart")

        order = Order.objects.create(
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address_line1=request.POST.get("address_line1"),
            address_line2=request.POST.get("address_line2", ""),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            postal_code=request.POST.get("postal_code"),
            country=request.POST.get("country"),
            total=cart_total,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                sku=item["sku"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=item["price"],
            )

        _send_confirmation_email(order)
        request.session["cart"] = {}
        request.session.modified = True
        return redirect("order_confirmation", pk=order.pk)

    return render(request, "pages/checkout.html", _build_cart_context(request))


def _send_confirmation_email(order):
    try:
        html = render_to_string("emails/order_confirmation.html", {"order": order})
        send_mail(
            subject=f"Order #{order.pk} confirmed – WebShop",
            message=f"Thank you {order.full_name}, order #{order.pk} totalling ${order.total} is confirmed.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send confirmation email for order #{order.pk}: {e}")


def order_confirmation(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "pages/order_confirmation.html", {"order": order})


# ═══════════════════════════════════════════════════════════
#  Static pages
# ═══════════════════════════════════════════════════════════

def about(request):
    return render(request, "pages/about.html")


def contact(request):
    sent = False
    error = False

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        try:
            send_mail(
                subject=f"[Webshop] {subject}",
                message=f"From: {name} {last_name} <{email}>\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=["contact@webshop.com"],
                fail_silently=False,
            )
            sent = True
        except Exception as e:
            logger.error(f"Contact mail failed: {e}")
            error = True

    return render(request, "pages/contact.html", {"sent": sent, "error": error})