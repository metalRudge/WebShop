from django.contrib import admin
from .models import Product,Category
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display      = ("sku_id", "product_name", "price", "availability", "category_list")
    filter_horizontal = ("categories",)
    search_fields     = ("sku_id", "product_name")
    list_filter       = ("availability", "categories")

    def category_list(self, obj):
        return ", ".join(c.name for c in obj.categories.all())
    category_list.short_description = "Categories"