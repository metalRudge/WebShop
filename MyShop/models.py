from django.db import models
from django.db.models import JSONField

class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):
    sku_id = models.CharField(max_length=64, primary_key=True)
    product_name = models.CharField(max_length=120)
    categories = models.ManyToManyField(Category,blank=True)
    description = models.TextField(max_length=255, blank=True)
    images_cdn = JSONField(blank=True, null=True,default=list)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=False)

    class Meta:
        db_table = 'products'
        ordering = ["product_name"]

    def __str__(self):
        return self.product_name + f"  sku: ({self.sku_id}) \n"

class Order(models.Model):

    STATUS_CHOICES = [
        ("pending",    "Pending"),
        ("processing", "Processing"),
        ("shipped",    "Shipped"),
        ("delivered",  "Delivered"),
        ("cancelled",  "Cancelled"),
    ]

    full_name     = models.CharField(max_length=120)
    email         = models.EmailField()
    phone         = models.CharField(max_length=30)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, default="")
    city          = models.CharField(max_length=100)
    state         = models.CharField(max_length=100)
    postal_code   = models.CharField(max_length=20)
    country       = models.CharField(max_length=100)
    total         = models.DecimalField(max_digits=10, decimal_places=2)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} – {self.full_name}"


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    sku          = models.CharField(max_length=50)
    product_name = models.CharField(max_length=200)
    quantity     = models.PositiveIntegerField()
    unit_price   = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"