import uuid
from django.utils import timezone
from django.db import models, transaction
from django.db.models import Max
from django.template.defaultfilters import slugify
from django.contrib import admin
from core.models import (
    User,
    Store,
)
from products.jwplayer import get_signed_player
from django.contrib.postgres.fields import JSONField
from core.models import UploadedImage


class ProductCategory(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    thumbnail_image = models.ForeignKey(UploadedImage, null=True,
                                        blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1} [order: {2}]".format(self.store.store_slug,
                                               self.name,
                                               self.order)

    class Meta:
        unique_together = ["store", "name"]
        ordering = ["name"]


class Product(models.Model):
    """
    A product sold by a store.
    """
    PRODUCT_TYPE_CHOICES = (
        ("course", "Course"),
        ("digital", "Digital Download"),
        ("bundle", "Product Bundle")
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE,
                              null=True, blank=True)
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    product_type = models.CharField(max_length=8, choices=PRODUCT_TYPE_CHOICES)
    free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    categories = models.ManyToManyField(ProductCategory, blank=True)
    thumbnail_image = models.ForeignKey(UploadedImage, null=True,
                                        blank=True, on_delete=models.CASCADE)
    order = models.IntegerField(null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    draft = models.BooleanField(default=True)

    schema = JSONField(default=list, blank=True)
    schema_draft = JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def pre_sale(self):
        """
        A product is in pre-sale if draft is false and
        the start date is greater than today.
        :return:
        """
        return all([
            self.draft is False,
            self.start_date is not None and self.start_date > timezone.now().date()
        ])

    @property
    def published(self):
        """
        A product is published if draft is false and
        the start date is less than or equal to today.
        :return:
        """
        return all([
            self.draft is False,
            self.start_date is None or self.start_date <= timezone.now().date()
        ])

    @property
    def formatted_price(self):
        if self.price:
            return self.store.currency_format.format(self.price)

        return None

    @property
    def content_items(self):
        return self.contentitem_set.filter(parent_item=None).order_by("order")

    @property
    def sections(self):
        return self.contentitem_set.filter(
            content_type="section", parent_item=None)

    @property
    def top_level_content_items(self):
        return self.contentitem_set.filter(
            parent_item=None).exclude(content_type="section")

    @property
    def dashboard_link(self):
        mapper = {
            "course": "courses",
            "digital": "downloads",
            "bundle": "bundles"
        }
        return "/{0}/{1}/".format(mapper[self.product_type], self.slug)

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            slug = slugify(self.name)

            counter = 1
            while True:
                try:
                    existing = Product.objects.get(
                        store=self.store, slug=slug)

                    if existing == self:
                        self.slug = slug
                        break
                    else:
                        slug = "{0}-{1}".format(counter, slug)
                        counter += 1

                except Product.DoesNotExist:
                    self.slug = slug
                    break

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} - {1} ({2})".format(
            self.store.name, self.name, self.product_type)

    class Meta:
        unique_together = [["store", "slug"]]


class ContentItem(models.Model):
    CONTENT_TYPE_CHOICES = (
        ("section", "Section"),
        ("text", "Text"),
        ("file", "File"),
        ("link", "Link"),
        ("video", "Video"),
        ("product", "Product")
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    parent_item = models.ForeignKey("ContentItem", null=True, blank=True,
                                    on_delete=models.CASCADE)
    content_type = models.CharField(max_length=8, choices=CONTENT_TYPE_CHOICES)
    title = models.CharField(max_length=256)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    content = models.TextField(null=True, blank=True)
    editor_content = JSONField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    presigned_url = models.URLField(null=True, blank=True)
    presigned_url_fields = JSONField(null=True, blank=True)
    file_path = models.CharField(max_length=1024, null=True, blank=True)
    file_name = models.CharField(max_length=256, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    media_id = models.CharField(max_length=64, null=True, blank=True)
    order = models.IntegerField(default=1)
    linked_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                       null=True, blank=True,
                                       related_name="linked_product")

    draft = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def content_items(self):
        if self.content_type != "section":
            return None

        return self.contentitem_set.all()

    @property
    def player_url(self):
        if self.media_id is None:
            return None

        return get_signed_player(self.media_id)

    @property
    def prev_in_course(self):
        if self.content_type == "section":
            return None

        if ContentItem.objects.filter(
                product=self.product,
                parent_item=self.parent_item,
                order__lt=self.order).exists():
            return ContentItem.objects.filter(
                product=self.product,
                parent_item=self.parent_item,
                order__lt=self.order).order_by("-order").first()

        elif ContentItem.objects.filter(
                product=self.product,
                parent_item=None,
                order__lt=self.parent_item.order).exists():
            parent_item = ContentItem.objects.filter(
                product=self.product,
                parent_item=None,
                order__lt=self.parent_item.order).order_by("-order").first()

            return ContentItem.objects.filter(
                product=self.product,
                parent_item=parent_item).order_by("-order").first()

        else:
            return None

    @property
    def next_in_course(self):
        if self.content_type == "section":
            return None

        if ContentItem.objects.filter(
                product=self.product,
                parent_item=self.parent_item,
                order__gt=self.order).exists():
            return ContentItem.objects.filter(
                product=self.product,
                parent_item=self.parent_item,
                order__gt=self.order).first()

        elif ContentItem.objects.filter(
                product=self.product,
                parent_item=None,
                order__gt=self.parent_item.order).exists():

            parent_item = ContentItem.objects.filter(
                product=self.product,
                parent_item=None,
                order__gt=self.parent_item.order).first()

            return ContentItem.objects.filter(
                product=self.product, parent_item=parent_item).first()

        else:
            return None

    def __str__(self):
        return "Product: {0} - {1} {2} | Order: {3}".format(
            self.product.uuid,
            self.content_type,
            self.uuid,
            self.order
        )

    class Meta:
        ordering = ["order"]


class Membership(models.Model):
    """
    A membership sold by a store.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE,
                              null=True, blank=True)
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True, null=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True,
                                blank=True)
    draft = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["store", "slug"]]


admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ContentItem)
admin.site.register(Membership)
