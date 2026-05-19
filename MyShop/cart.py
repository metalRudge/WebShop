# cart.py
from decimal import Decimal

def get_cart(request) -> dict:
    return request.session.setdefault("cart", {})

def save_cart(request, cart: dict):
    request.session["cart"] = cart
    request.session.modified = True

def add_to_cart(request, product):
    cart = get_cart(request)
    sku = product.sku_id
    unit_price = product.price
 
    if sku in cart:
        if Decimal(str(cart[sku]["price"])) != unit_price:
            logger.warning(f"Price changed for {sku}, updating.")
            cart[sku]["price"] = str(unit_price)
        cart[sku]["quantity"] += 1
    else:
        cart[sku] = {
            "product_name": product.product_name,
            "price": str(unit_price),
            "quantity": 1
        }

    save_cart(request, cart)

def remove_from_cart(request, sku_id: str):
    cart = get_cart(request)
    cart.pop(sku_id, None)
    save_cart(request, cart)

def increase_quantity(request, sku_id: str):
    cart = get_cart(request)
    if sku_id in cart:
        cart[sku_id]["quantity"] += 1
        save_cart(request, cart)

def decrease_quantity(request, sku_id: str):
    cart = get_cart(request)
    if sku_id in cart:
        if cart[sku_id]["quantity"] <= 1:
            cart.pop(sku_id)
        else:
            cart[sku_id]["quantity"] -= 1
        save_cart(request, cart)

def get_cart_meta(request) -> dict:
    cart = get_cart(request)
    count = sum(item["quantity"] for item in cart.values())
    return {"meta": {"cart_count": count}}