import humanize
from rest_framework import serializers
from products.models import (
    ProductCategory,
    Product,
    ContentItem,
    Membership
)


class ProductCategorySerializer(serializers.ModelSerializer):
    """

    """
    class Meta:
        model = ProductCategory
        fields = [
            "uuid",
            "name",
            "description",
            "thumbnail_image",
            "order"
        ]


class ProductSerializer(serializers.ModelSerializer):
    UNIQUE_SLUG_MSG = "This permalink is already taken. Please choose another."
    NO_CURRENCY_SET_MSG = "The store currency is not set."
    NO_PRICE_SET_MESSAGE = "The price of the product is not set."

    uuid = serializers.UUIDField(required=False, read_only=True)
    formatted_price = serializers.SerializerMethodField()
    product_type_display = serializers.SerializerMethodField()
    categories = ProductCategorySerializer(read_only=True, many=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_formatted_price(self, obj):
        return obj.formatted_price

    def get_product_type_display(self, obj):
        return obj.get_product_type_display()

    def validate_slug(self, value):
        """

        :param value:
        :return:
        """
        if Product.objects.filter(store=self.instance.store,
                                  slug=value).exists():
            product = Product.objects.get(
                store=self.instance.store,
                slug=value)

            if product.pk != self.instance.id:
                raise serializers.ValidationError(self.UNIQUE_SLUG_MSG)

        return value

    def validate_draft(self, value):
        """
        If draft is being set to false, checks that:

        - The store has a currency set.
        - The product is free or has a price set.

        :param value:
        :return:
        """
        if not value:
            if not self.instance.store.currency:
                raise serializers.ValidationError(self.NO_CURRENCY_SET_MSG)

            if not self.instance.free and self.instance.price is None:
                raise serializers.ValidationError(self.NO_PRICE_SET_MESSAGE)

        return value

    class Meta:
        model = Product
        fields = [
            "uuid",
            "name",
            "slug",
            "description",
            "product_type",
            "product_type_display",
            "free",
            "price",
            "formatted_price",
            "start_date",
            "categories",
            "thumbnail_image",
            "order",
            "draft",
            "schema",
            "schema_draft",
            "created_at",
            "updated_at"
        ]


class ContentItemSerializer(serializers.ModelSerializer):
    FILE_MISSING_MSG = "You must select a file."
    URL_MISSING_MSG = "You must provide a URL."

    uuid = serializers.UUIDField(required=False, read_only=True)
    url = serializers.URLField(required=False, allow_blank=False)
    linked_product = ProductSerializer(required=False, allow_null=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)
    product_uuid = serializers.SerializerMethodField()
    parent_uuid = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    file_size_readable = serializers.SerializerMethodField()

    def get_product_uuid(self, obj):
        return obj.product.uuid

    def get_parent_uuid(self, obj):
        return obj.parent_item.uuid if obj.parent_item else None

    def get_children(self, obj):
        return ContentItemSerializer(obj.contentitem_set, many=True).data

    def get_file_size_readable(self, obj):
        """

        :param obj:
        :return:
        """
        if obj.file_size:
            return humanize.naturalsize(obj.file_size)

        return None

    def validate(self, attrs):
        """

        :param attrs:
        :return:
        """
        request = self.context['request']

        if request.method == "POST":
            content_type = attrs.get("content_type")
            file_name = attrs.get("file_name")
            url = attrs.get("url")

            if content_type == "file" and file_name is None:
                raise serializers.ValidationError({
                    "file_name": self.FILE_MISSING_MSG
                })
            elif content_type == "link" and url is None:
                raise serializers.ValidationError({
                    "url": self.URL_MISSING_MSG
                })

        return attrs

    class Meta:
        model = ContentItem
        fields = [
            "uuid",
            "product_uuid",
            "parent_uuid",
            "title",
            "content_type",
            "content",
            "editor_content",
            "url",
            "presigned_url",
            "presigned_url_fields",
            "file_path",
            "file_name",
            "file_size",
            "file_size_readable",
            "player_url",
            "media_id",
            "order",
            "linked_product",
            "draft",
            "children",
            "created_at",
            "updated_at"
        ]


class MoveContentItemSerializer(serializers.Serializer):
    """

    """
    parent_uuid = serializers.UUIDField(required=False, allow_null=True)
    position = serializers.IntegerField()


class MoveProductCategorySerializer(serializers.Serializer):
    """

    """
    position = serializers.IntegerField()


class MoveProductSerializer(serializers.Serializer):
    """

    """
    position = serializers.IntegerField()


class MembershipSerializer(serializers.ModelSerializer):
    """

    """
    uuid = serializers.UUIDField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = Membership
        fields = [
            "uuid",
            "name",
            "slug",
            "price",
            "draft",
            "created_at",
            "updated_at"
        ]


class AddProductToBundleSerializer(serializers.Serializer):
    product_uuid = serializers.UUIDField()

    def validate_product_uuid(self, val):
        if Product.objects.filter(store=self.context['request'].user.store,
                                  uuid=val).exists():
            return val

        raise serializers.ValidationError(
            "Product does not exist.")