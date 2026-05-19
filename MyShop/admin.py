from django.contrib import admin
from .models import Product
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku_id', 'product_name', 'price', 'availability')
    search_fields = ('sku_id', 'product_name')