from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from core.models import (
    Store,
    User
)


class Appearance(models.Model):
    DEFAULTS = {
        "primary_colour": "",
        "background_colour": "",
        "heading_colour": "",
        "text_colour": "",
        "button_colour": "",
        "button_text_colour": "",
        "heading_font": "",
        "body_font": ""
    }

    store = models.OneToOneField(Store, on_delete=models.CASCADE)
    primary_colour = models.CharField(
        max_length=6, default=DEFAULTS["primary_colour"])
    background_colour = models.CharField(
        max_length=6, default=DEFAULTS["background_colour"])
    heading_colour = models.CharField(
        max_length=6, default=DEFAULTS["heading_colour"])
    text_colour = models.CharField(
        max_length=6, default=DEFAULTS["text_colour"])
    button_colour = models.CharField(
        max_length=6, default=DEFAULTS["button_colour"])
    button_text_colour = models.CharField(
        max_length=6, default=DEFAULTS["button_text_colour"])
    heading_font = models.CharField(
        max_length=64, default=DEFAULTS["heading_font"])
    body_font = models.CharField(
        max_length=64, default=DEFAULTS["body_font"])


@receiver(post_save, sender=Store)
def store_post_save(sender, instance, **kwargs):
    """

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if kwargs["created"]:
        Appearance.objects.create(store=instance)


admin.site.register(Appearance)