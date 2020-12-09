import uuid
from django.db import models
from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import (
    Store,
    User
)


class MessagingSettings(models.Model):
    """

    """
    CHAT_DISPLAY_AS_CHOICES = (
        ("STORE", "Name of store"),
        ("USER", "User's full name"),
        ("CUSTOM", "Custom value")
    )

    CHAT_STATUS_CHOICES = (
        ("ONLINE", "Online"),
        ("AWAY", "Away"),
        ("HIDDEN", "Hidden")
    )

    CHAT_AVAILABLE_TO_CHOICES = (
        ("NOBODY", "Nobody"),
        ("CUSTOMER", "Customers"),
        ("STORE", "Everybody")
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.OneToOneField(Store, on_delete=models.CASCADE)

    chat_display_as = models.CharField(
        max_length=8, choices=CHAT_DISPLAY_AS_CHOICES, default="STORE")
    chat_display_name = models.CharField(max_length=64, null=True, blank=True)
    default_status = models.CharField(
        max_length=8, choices=CHAT_STATUS_CHOICES, default="ONLINE")
    chat_available_to = models.CharField(
        max_length=8, choices=CHAT_AVAILABLE_TO_CHOICES, default="CUSTOMER")
    play_sounds = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Store)
def store_post_save(sender, instance, **kwargs):
    if kwargs["created"]:
        MessagingSettings.objects.create(store=instance)


class Chat(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def messages(self):
        return Message.objects.filter(chat=self).order_by("created_at")

    class Meta:
        unique_together = ["store", "user"]



class Message(models.Model):
    SENDER_CHOICES = (
        ("STORE", "Store"),
        ("USER", "User")
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.CharField(max_length=8, choices=SENDER_CHOICES, default="USER")
    message = models.TextField()
    seen = models.BooleanField(default=False)
    acknowledged = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]



admin.site.register(MessagingSettings)
admin.site.register(Chat)
admin.site.register(Message)
