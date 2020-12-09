import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.contrib.postgres.fields import JSONField
from products.jwplayer import get_signed_player


class SupportedCurrency(models.Model):
    """

    """
    code = models.CharField(max_length=3, unique=True)
    symbol = models.CharField(max_length=3, null=True, blank=True)
    name = models.CharField(max_length=64)
    multiple = models.IntegerField(default=100)
    format_string = models.CharField(max_length=8, null=True, blank=True)
    order = models.IntegerField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]


class Store(models.Model):
    """

    """
    SECTION_LAYOUT_CHOICES = (("LIST", "List"), ("GRID", "Grid"),)

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    owner = models.OneToOneField("User", on_delete=models.CASCADE)
    name = models.CharField(max_length=256, null=True, blank=True)
    store_slug = models.SlugField(unique=True, null=True, blank=True)

    currency = models.CharField(max_length=3, default="USD")
    tax_address = models.TextField(null=True, blank=True)
    collect_tax_addresses = models.BooleanField(default=False)
    timezone = models.CharField(max_length=64, null=True,
                                blank=True, default="UTC")
    language = models.CharField(max_length=2, default="en")

    subdomain = models.CharField(max_length=256, unique=True,
                                 null=True, blank=True)
    custom_domain = models.URLField(null=True, blank=True)

    schema = JSONField(default=list, blank=True)
    schema_draft = JSONField(default=list, blank=True)

    product_section_layout = models.CharField(default="LIST", max_length=8,
                                              choices=SECTION_LAYOUT_CHOICES)
    category_section_layout = models.CharField(default="LIST", max_length=8,
                                              choices=SECTION_LAYOUT_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_uploaded_image_url(self, image_uuid):
        """

        :param image_uuid:
        :return:
        """
        try:
            image = UploadedImage.objects.get(store=self, uuid=image_uuid)
            return image.url
        except UploadedImage.DoesNotExist:
            return None

    def get_uploaded_video_player_url(self, video_uuid):
        """

        :param video_uuid:
        :return:
        """
        try:
            video = UploadedVideo.objects.get(store=self, uuid=video_uuid)
            return video.player_url
        except UploadedVideo.DoesNotExist:
            return None

    @property
    def email_subscribe_url(self):
        """
        return
        :return:
        """
        return "http://teststore.courses.test:8000/email_subscribe/"

    @property
    def display_name(self):
        if self.name:
            return self.name

        return "{0}'s Store".format(self.owner.full_name)

    @property
    def currency_format(self):
        try:
            currency = SupportedCurrency.objects.get(code=self.currency)
            return currency.format_string

        except SupportedCurrency.DoesNotExist:
            return "{0}"

    def save(self, *args, **kwargs):
        if not self.id and not self.store_slug:
            slug = slugify(self.owner.full_name)

            counter = 1
            while True:
                try:
                    existing = Store.objects.get(store_slug=slug)

                    if existing == self:
                        self.store_slug = slug
                        break
                    else:
                        slug = "{0}-{1}".format(counter, slug)
                        counter += 1

                except Store.DoesNotExist:
                    self.store_slug = slug
                    break

        super(Store, self).save(*args, **kwargs)


class UploadedImage(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey("Store", on_delete=models.CASCADE)
    name = models.CharField(max_length=512, null=True, blank=True)
    content = models.BinaryField(max_length=5120,
                                 null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def url(self):
        """

        :return:
        """
        return "http://teststore.courses.test:8000/images/{0}/".format(
            str(self.uuid))


class UploadedVideo(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey("Store", on_delete=models.CASCADE)
    name = models.CharField(max_length=512, null=True, blank=True)
    presigned_url = models.URLField(null=True, blank=True)
    presigned_url_fields = JSONField(null=True, blank=True)
    media_id = models.CharField(max_length=64, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def player_url(self):
        if self.media_id is None:
            return None

        return get_signed_player(self.media_id)



class NotificationSettings(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.OneToOneField("Store", on_delete=models.CASCADE)

    # Sales
    new_free_product_email = models.BooleanField(default=True)
    new_sale_email = models.BooleanField(default=True)
    new_membership_email = models.BooleanField(default=True)
    cancel_membership_email = models.BooleanField(default=True)

    # Messaging
    new_message_email = models.BooleanField(default=True)
    new_message_app = models.BooleanField(default=True)

    # Interactions
    course_comment_email = models.BooleanField(default=True)
    course_completed_email = models.BooleanField(default=True)


class User(AbstractUser):
    """
    An user who can either be a shop, an administrator,
    or an affiliate.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'))
    customer_of = models.ForeignKey(Store, null=True,
                                    blank=True, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    @property
    def is_store_owner(self):
        return self.store is not None

    @property
    def is_customer(self):
        return self.customer is not None

    def send_password_reset_email(self):
        """
        Sends a password reset email to the user.

        :return:
        """


    def __str__(self):
        return self.email

    class Meta:
        unique_together = ["email", "customer_of"]


class PasswordResetKey(models.Model):
    """
    Key for password reset.
    """
    store = models.ForeignKey(Store, on_delete=models.CASCADE,
                              null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64)
    used = models.BooleanField(default=False)
    expires = models.DateField()


@receiver(post_save, sender=User)
def user_post_save(sender, instance, **kwargs):
    """

    :param sender:
    :param kwargs:
    :return:
    """
    if kwargs["created"] and instance.customer_of is None:
        Store.objects.create(owner=instance)


@receiver(post_save, sender=Store)
def store_post_save(sender, instance, **kwargs):
    if kwargs["created"]:
        NotificationSettings.objects.create(store=instance)


admin.site.register(SupportedCurrency)
admin.site.register(Store)
admin.site.register(User)
admin.site.register(NotificationSettings)
admin.site.register(UploadedImage)
admin.site.register(UploadedVideo)
