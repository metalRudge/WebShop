import logging
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

CART_SESSION_KEY = 'cart'


def _recalculate_meta(cart: dict) -> dict:
    """Recalculate the cart total price and item count."""
    total_price = Decimal('0.00')
    total_items = 0
    for key, item in cart.items():
        if key == '_meta':
            continue
        try:
            total_price += Decimal(item['price']) * item['quantity']
            total_items += item['quantity']
        except (KeyError, InvalidOperation) as e:
            logger.error(f"Error calculating cart totals for item '{key}': {e}")
            continue
    return {
        'cart_count': total_items,
        'cart_total': total_price,
    }


def get_cart(request: object) -> dict:
    return request.session.get(CART_SESSION_KEY, {})


def get_cart_meta(request: object) -> dict:
    return get_cart(request).get('_meta', {'cart_count': 0, 'cart_total': Decimal('0.00')})


def save_cart(request: object, cart: dict) -> None:
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True

def add_to_cart(request: object, product) -> dict:
    """
    Adds a product to the session cart.
    Validates stock and re-validates price against current DB value.
    Returns updated _meta dict or raises RuntimeError on failure.
    """
    try: # catch any unexpected errors to prevent session corruption and log them
        try: #ensure session exists - if not, create it. 
            if not request.session.session_key:
                request.session.create()
                logger.info("No existing session found; created a new session.")
        except Exception as e:
            logger.info(f"New Session creation failed - : {e}")
            raise RuntimeError("Failed to find or create session for cart,") from e

        # Stock guard
        if hasattr(product, 'stock') and product.stock <= 0:
            raise ValueError(f"Product {product.sku_id} is out of stock.")

        # Validate price from DB
        try:
            unit_price = Decimal(str(product.price)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, TypeError) as e:
            raise ValueError(f"Invalid price for product {product.sku_id}: {e}")

        cart = get_cart(request)
        sku = product.sku_id

        if sku in cart:
            # Stock guard against over-adding
            if hasattr(product, 'stock') and cart[sku]['quantity'] >= product.stock:
                raise ValueError(f"Cannot add more of {product.sku_id}, insufficient stock.")

            # Re-validate price — update if it changed since last add
            stored_price = Decimal(str(cart[sku]['price']))
            if stored_price != unit_price:
                logger.warning(
                    f"Price changed for {sku}: was {stored_price}, now {unit_price}. Updating."
                )
                cart[sku]['price'] = str(unit_price)

            cart[sku]['quantity'] += 1
        else:
            cart[sku] = {
                'product_name': product.product_name,
                'price': str(unit_price),
                'quantity': 1,
            }

        cart['_meta'] = _recalculate_meta(cart)
        save_cart(request, cart)

        return cart['_meta']

    except ValueError as e:
        logger.warning(f"Cart add rejected for {product.sku_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to add to session cart for SKU {product.sku_id}: {e}")
        print(f"Failed to add to session cart: {e}")
        raise RuntimeError("Failed to add item to cart.") from e