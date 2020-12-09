import uuid
from django.contrib import admin
from django.db import models

from core.models import Store

from saas_template.settings import (
    APP_DOMAIN
)


TEMPLATE_TYPES = (
    ("INDEX", "Index"),
    ("PRODUCT", "Product"),
    ("PAGE", "Page")
)


SECTION_TYPES = (
    ("BIO", "Bio"),
    ("FAQ", "FAQ"),
    ("IMAGE_WITH_TEXT", "Image with text"),
    ("NEWSLETTER", "Newsletter"),
    ("TOC", "Table of contents"),
    ("TESTIMONIALS", "Testimonials"),
    ("TEXT", "Text"),
    ("VIDEO_WITH_TEXT", "Video with text"),
    ("CATEGORIES", "Categories"),
    ("PRODUCTS", "Products"),
    ("COLUMNS", "Columns"),
)


ASSET_TYPES = (
    ("JS", "Javascript"),
    ("CSS", "CSS"),
    ("IMG", "Image"),
    ("OTHER", "Other"),
)


# Models.that duplicate the theme for the site.

class SiteTheme(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=512)
    live = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def variables(self):
        return self.sitethemevariable_set

    @property
    def templates(self):
        return self.sitethemetemplate_set

    @property
    def sections(self):
        return self.sitethemesection_set

    @property
    def assets(self):
        return self.sitethemeasset_set

    def get_asset_url(self, asset_name):
        try:
            asset = SiteThemeAsset.objects.get(site_theme=self,
                                               name=asset_name)
            return asset.url

        except SiteThemeAsset.DoesNotExist:
            return None

    def __str__(self):
        return "{0} - {1}".format(self.store.display_name, self.name)

    class Meta:
        unique_together = ["store", "name"]
        ordering = ["name"]


class SiteThemeVariable(models.Model):
    """

    """
    VARIABLE_TYPE_CHOICES = (
        ("STRING", "String"),
        ("INT", "Integer"),
        ("HEXCOLOR", "Hex colour code"),
        ("URL", "URL"),
        ("IMAGE", "Image"),
        ("BOOL", "Boolean")
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    site_theme = models.ForeignKey(SiteTheme, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=512)
    binary_value = models.BinaryField(null=True, blank=True) # TODO: max_length
    variable_type = models.CharField(max_length=8,
                                     choices=VARIABLE_TYPE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}: {2} [{3}]".format(
            self.site_theme.store.display_name,
            self.site_theme.name,
            self.name,
            self.get_variable_type_display()
        )

    class Meta:
        unique_together = ["site_theme", "name"]
        ordering = ["name"]


class SiteThemeTemplate(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    site_theme = models.ForeignKey(SiteTheme, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    template_type = models.CharField(max_length=16, choices=TEMPLATE_TYPES,
                                     null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}: {2}".format(
            self.site_theme.store.display_name,
            self.site_theme.name,
            self.name
        )

    class Meta:
        unique_together = ["site_theme", "name"]


class SiteThemeSection(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    site_theme = models.ForeignKey(SiteTheme, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    section_type = models.CharField(max_length=16, choices=SECTION_TYPES,
                                     null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} - {1}: {2}".format(
            self.site_theme.store.display_name,
            self.site_theme.name,
            self.name
        )

    class Meta:
        unique_together = ["site_theme", "name"]


class SiteThemeAsset(models.Model):
    """

    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    site_theme = models.ForeignKey(SiteTheme, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    asset_type = models.CharField(max_length=16, choices=ASSET_TYPES,
                                    null=True, blank=True)
    content = models.BinaryField(max_length=5120,
                                 null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def editable(self):
        return self.asset_type not in [None, "IMG", "OTHER"]

    @property
    def url(self):
        return "http://teststore.courses.test:8000/themes/{0}/assets/{1}".format(
            str(self.site_theme.uuid),
            self.name
        )

    @property
    def content_type(self):
        content_types = {
            "JS": "text/javascript",
            "CSS": "text/css",
            "IMG": "image/jpg"
        }

        return content_types.get(self.asset_type, "application/octet-stream")

    def __str__(self):
        return "{0} - {1}: {2}".format(
            self.site_theme.store.display_name,
            self.site_theme.name,
            self.name
        )

    class Meta:
        unique_together = ["site_theme", "name"]


admin.site.register(SiteTheme)
admin.site.register(SiteThemeVariable)
admin.site.register(SiteThemeTemplate)
admin.site.register(SiteThemeSection)
admin.site.register(SiteThemeAsset)
