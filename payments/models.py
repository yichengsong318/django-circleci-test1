import uuid
from django.contrib import admin
from django.db import models
from django.core.management.utils import get_random_secret_key
from core.models import (
    Store
)
from customers.models import (
    Sale,
    Invoice
)

class StripeConnect(models.Model):
    """
    A connection between CoursePropeller's
    Stripe account and a store's account.
    """
    store = models.OneToOneField(Store, on_delete=models.CASCADE)
    redirect_state = models.CharField(max_length=50, unique=True)
    scope = models.CharField(max_length=32, default="read_write")
    connected_account_id = models.CharField(
        max_length=128, null=True, blank=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_unique_secret_key(self):
        """

        :return:
        """
        s = get_random_secret_key()

        while True:
            try:
                existing = StripeConnect.objects.get(
                    redirect_state=s)

                if existing != self:
                    s = get_random_secret_key()

            except StripeConnect.DoesNotExist:
                break

        return s

    def save(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        self.redirect_state = self.get_unique_secret_key()
        super(StripeConnect, self).save(*args, **kwargs)


class Payment(models.Model):
    """
    A payment made for something a store sold to one of its customers.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE,
                                null=True, blank=True)
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE,
                                   null=True, blank=True)

    stripe_payment_intent_id = models.CharField(max_length=32, unique=True,
                                                null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


admin.site.register(StripeConnect)
admin.site.register(Payment)
