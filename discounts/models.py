import uuid
from django.db import models
from django.contrib import admin
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from core.models import Store
from customers.models import (
    Customer,
    Sale,
    MembershipSubscription
)


class DiscountCode(models.Model):
    """
    This model represents a discount code. A discount code can be either
    active or inactive, and it has a max_usages property.
    """
    REDUCTION_TYPE_CHOICES = (
        ("amount", "Amount"),
        ("percent", "Percentage")
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    reduction_type = models.CharField(max_length=8,
                                      choices=REDUCTION_TYPE_CHOICES)
    reduction = models.DecimalField(max_digits=6, decimal_places=2,
                                    validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)
    expiry = models.DateTimeField(null=True, blank=True)
    max_usages = models.IntegerField(null=True, blank=True,
                                     validators=[MinValueValidator(1)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def num_usages(self):
        return self.discountcodeusage_set.count()

    @property
    def formatted_reduction(self):
        if self.reduction_type == "percent":
            return "{0}%".format(self.reduction)
        else:
            return self.store.currency_format.format(self.reduction)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ["code"]
        unique_together = ["store", "code", "active"]


class DiscountCodeUsage(models.Model):
    """
    This model

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    discount_code = models.ForeignKey(DiscountCode, on_delete=models.CASCADE)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE,
                                null=True, blank=True)
    subscription = models.OneToOneField(MembershipSubscription,
                                        on_delete=models.CASCADE,
                                        null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["discount_code", "sale"],
                           ["discount_code", "subscription"]]


admin.site.register(DiscountCode)
admin.site.register(DiscountCodeUsage)
