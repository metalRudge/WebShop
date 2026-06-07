from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import User

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


class AddressBase(models.Model):
    phone         = models.CharField(max_length=30)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, default="")
    city          = models.CharField(max_length=100)
    state            = models.CharField(max_length=100)
    postal_code   = models.CharField(max_length=20)
    country       = models.CharField(max_length=100)
    created_at    = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True  # no DB table, just shared field definitions

class Address(AddressBase):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    label = models.CharField(max_length=50, blank=True, default="")
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        label = f" ({self.label})" if self.label else ""
        return f"{self.user.username}{label} - {self.city}, {self.country}"
    

class Order(AddressBase):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="orders")
    full_name = user.name
    total = models.DecimalField(max_digits=100,decimal_places=2)

    STATUS_CHOICES = [
        ("pending",    "Pending"),
        ("processing", "Processing"),
        ("shipped",    "Shipped"),
        ("delivered",  "Delivered"),
        ("cancelled",  "Cancelled"),
    ]
    
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending")

    @property
    def customer_name(self):
        if not self.user:
            return "Guest"
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def customer_email(self):
        return self.user.email if self.user else ""

    def __str__(self):
        return f"{self.pk} – {self.state}, {self.city}"  


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items",)
    sku          = models.CharField(max_length=50)
    product_name = models.CharField(max_length=200)
    quantity     = models.PositiveIntegerField()
    unit_price   = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"