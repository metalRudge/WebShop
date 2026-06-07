from django.urls import path
from MyShop import views

urlpatterns = [
    path("", views.about, name="home"),
    path("products/", views.products, name="products"),
    path("products/<str:sku_id>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("search/", views.search, name="search"),
    path("order/<int:pk>/confirmation/", views.order_confirmation, name="order_confirmation"),
    path("contact/", views.contact, name="contact"),

    path("auth/login/", views.login, name="login"),
    path("auth/logout/", views.logout, name="logout"),
    path("auth/register/", views.register, name="register"),
    path("auth/token/refresh/", views.token_refresh, name="token_refresh"),
    path("auth/account/", views.account, name="account"),
]