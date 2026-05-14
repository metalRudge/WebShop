"""Views for the `MyShop` app.

Phase 1 only ships a homepage. Function-based views are used because
they are the simplest fit for a static template render. Switch to
class-based views only when shared behavior justifies the abstraction.
"""

from django.shortcuts import render
def products(request):
    if(request.headers.get('Hx-Request') == 'true'):
        return render(request, 'partials/product_content.html')
    """Render the products page."""
    context = {
        'phase': 'Phase 2',
        'title': 'Webshop - Products',
    }
    return render(request, 'pages/products.html', context)

def home(request):
    """Render the Phase 1 Hello World / project-start page."""
    context = {
        'phase': 'Phase 1',
        'title': 'Webshop - Hello World',
    }
    return render(request, 'pages/home.html', context)
