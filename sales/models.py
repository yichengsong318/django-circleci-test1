import uuid
from django.db import models
from django.contrib import admin
from core.models import Store
from products.models import Product
from customers.models import Customer


class Sale(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["store", "customer", "product"]


admin.site.register(Sale)
