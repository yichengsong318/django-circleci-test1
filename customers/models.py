import uuid
from django.db import models
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from core.models import (
    Store,
    User
)

from products.models import (
    Product,
    Membership
)


class Customer(models.Model):
    """
    A customer of a store. This is linked to a user.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'))
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                null=True, blank=True)

    first_name = models.CharField(max_length=30, null=True, blank=True)
    accepts_marketing = models.BooleanField(default=False)

    stripe_customer_id = models.CharField(max_length=32, unique=True,
                                          null=True, blank=True)
    stripe_payment_method_id = models.CharField(max_length=32,
                                                null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def sales(self):
        return self.sale_set.all()

    class Meta:
        unique_together = ["store", "email"]


class Sale(models.Model):
    """
    A sale of a product to a customer by a store. The existence of a sale
    grants the customer access to the product within the store.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    was_free = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["store", "customer", "product"]


class MembershipSubscription(models.Model):
    """
    A customer's subscription to a membership sold by a store.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    valid_until = models.DateField(null=True, blank=True)

    stripe_subscription_id = models.CharField(max_length=32, unique=True,
                                              null=True, blank=True)

    stripe_product_id = models.CharField(max_length=32, null=True, blank=True)
    stripe_subscription_status = models.CharField(max_length=32,
                                                  null=True, blank=True)
    latest_invoice_payment_intent_status = models.CharField(
        max_length=32, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def invoices(self):
        return self.invoice_set.order_by("-period_end_date").all()


class Invoice(models.Model):
    """
    An invoice for a membership from a store to its customer.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        MembershipSubscription, on_delete=models.CASCADE)

    stripe_invoice_id = models.CharField(max_length=32, unique=True,
                                         null=True, blank=True)

    due_date = models.DateTimeField()
    period_start_date = models.DateTimeField()
    period_end_date = models.DateTimeField()

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)

    status = models.CharField(max_length=16)
    paid = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(MembershipSubscription)
admin.site.register(Invoice)
