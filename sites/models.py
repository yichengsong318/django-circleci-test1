import uuid
from django.db import models
from django.contrib import admin
from core.models import Store
from products.models import Product
from django.contrib.postgres.fields import JSONField


class Page(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    slug = models.SlugField()
    title = models.CharField(max_length=512, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    schema = JSONField(default=list, blank=True)
    schema_draft = JSONField(default=list, blank=True)
    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}".format(self.store.display_name, self.title)

    class Meta:
        unique_together = ["store", "slug"]
        ordering = ["title"]


admin.site.register(Page)


