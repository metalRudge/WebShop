
from django.urls import path

from MyShop import views

app_name = 'MyShop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
]
