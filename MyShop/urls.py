
from django.urls import path

from MyShop import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('products/<str:sku_id>/', views.product_detail, name='product_detail'),
]
