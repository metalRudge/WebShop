from django.contrib import admin
from .models import Product,Category,Order,OrderItem
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

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("sku", "product_name", "quantity", "unit_price", "subtotal")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "city", "country", "status", "created_at")
    list_filter = ("status", "country", "created_at")
    search_fields = ("id", "user__username", "city", "postal_code")
    inlines = [OrderItemInline]

    readonly_fields = (
        "user",
        "phone",
        "address_line1",
        "address_line2",
        "city",
        "state",
        "postal_code",
        "country",
        "created_at",
    )

    fieldsets = (
        ("Order", {
            "fields": ("user", "status", "created_at"),
        }),
        ("Shipping", {
            "fields": (
                "phone",
                "address_line1",
                "address_line2",
                "city",
                "state",
                "postal_code",
                "country",
            ),
        }),
    )