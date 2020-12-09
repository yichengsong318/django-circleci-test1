from django.db import models
from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Store

EMAIL_OPT_IN_DEFAULT = "I consent to receive updates about more awesome products."

class EmailMarketingSettings(models.Model):
    """

    """
    store = models.OneToOneField(Store, on_delete=models.CASCADE)
    mailing_address = models.TextField(null=True, blank=True)
    double_opt_in = models.BooleanField(default=True)
    opt_in_text = models.TextField(null=True, blank=True, default=EMAIL_OPT_IN_DEFAULT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Store)
def store_post_save(sender, instance, **kwargs):
    if kwargs["created"]:
        EmailMarketingSettings.objects.create(store=instance)


class EmailSubscriber(models.Model):
    """

    """
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["store", "email"]


admin.site.register(EmailMarketingSettings)
admin.site.register(EmailSubscriber)

