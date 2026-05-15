from django.db import models
from django.db.models import JSONField
class Product(models.Model):
    sku_id = models.CharField(max_length=64, primary_key=True)
    product_name = models.CharField(max_length=120)
    description = models.TextField(max_length=255, blank=True)
    images_cdn = JSONField(blank=True, null=True,default=list)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField(default=False)

    class Meta:
        db_table = 'products'
        ordering = ["product_name"]

    def __str__(self):
        return self.product_name + f"  sku: ({self.sku_id}) \n"
