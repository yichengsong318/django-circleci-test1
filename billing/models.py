import stripe
from django.db import models
from django.contrib import admin
from core.models import Store
from customers.models import (
    Customer,
    MembershipSubscription,
    Invoice
)

from saas_template.settings import (
    STRIPE_SECRET_KEY
)


stripe.api_key = STRIPE_SECRET_KEY


class StripeCustomer(models.Model):
    """
    A store's Stripe customer record.
    """
    store = models.OneToOneField(Store, models.CASCADE)
    stripe_customer_id = models.CharField(max_length=32, null=True, blank=True)
    stripe_payment_method_id = models.CharField(max_length=32, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subscription(self):
        try:
            return StripeSubscription.objects.get(stripe_customer=self)
        except StripeSubscription.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        if not self.stripe_customer_id:
            try:
                customer = stripe.Customer.create(email=self.store.owner.email)
                self.stripe_customer_id = customer.id
            except Exception as ex:
                pass

        super(StripeCustomer, self).save(*args, **kwargs)


class StripeSubscription(models.Model):
    """
    A store's subscription to CoursePropeller
    """
    stripe_customer = models.OneToOneField(StripeCustomer, models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=32, null=True, blank=True)
    stripe_product_id = models.CharField(max_length=32, null=True, blank=True)
    plan = models.CharField(max_length=32, null=True, blank=True)
    status = models.CharField(max_length=32, null=True, blank=True)
    latest_invoice_payment_intent_status = models.CharField(
        max_length=32, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StripeInvoice(models.Model):
    """
    An invoice sent to a store by CoursePropeller
    """
    stripe_invoice_id = models.CharField(max_length=32, null=True, blank=True)
    stripe_subscription = models.ForeignKey(
        StripeSubscription, on_delete=models.CASCADE)

    due_date = models.DateTimeField()
    period_start_date = models.DateTimeField()
    period_end_date = models.DateTimeField()

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)

    status = models.CharField(max_length=16)
    paid = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


admin.site.register(StripeCustomer)
admin.site.register(StripeSubscription)
admin.site.register(StripeInvoice)