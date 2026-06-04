from django.urls import path
from MyShop import views

urlpatterns = [
    path('', views.about, name='home'),
    path('products/', views.products, name='products'),
    path('products/<str:sku_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('search/',views.search,name='search')
]
