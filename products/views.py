import os
import boto3
import jwplatform
from botocore.exceptions import ClientError
from django.db import transaction
from django.db.models import Max
from django.views import View
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import (
    views,
    parsers
)
from rest_framework.response import Response
from rest_framework.decorators import action
from storages.backends.s3boto3 import S3Boto3Storage
from core.models import (
    User,
    Store
)
from products.models import (
    ProductCategory,
    Product,
    ContentItem
)
from products.serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ContentItemSerializer,
    MoveContentItemSerializer,
    MoveProductCategorySerializer,
    MoveProductSerializer,
    AddProductToBundleSerializer
)
from customers.models import Customer
from customers.serializers import CustomerSerializer
from saas_template.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    JWPLAYER_KEY,
    JWPLAYER_SECRET
)


def create_presigned_post(bucket_name, object_name,
                          fields=None, conditions=None, expiration=3600):
    """
    Generate a presigned URL S3 POST request to upload a file

    :param bucket_name: string
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     Fields=fields,
                                                     Conditions=conditions,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        return None

    return response


def find_free_file_path(user_uuid, product_uuid, filename):
    """

    :param user_uuid:
    :param product_uuid:
    :param filename:
    :return:
    """
    bucket_path = os.path.join(
        "user_upload_files",
        user_uuid,
        product_uuid,
        filename
    )

    storage = S3Boto3Storage()

    counter = 1
    while True:
        if not storage.exists(bucket_path):
            break

        bucket_path = os.path.join(
            "user_upload_files",
            user_uuid,
            product_uuid,
            "{0}-{1}".format(counter, filename)
        )

        counter += 1

    return bucket_path


def get_new_content_item_order(product, parent_item):
    results = ContentItem.objects.filter(
        product=product,
        parent_item=parent_item).aggregate(Max('order'))

    max_order = results['order__max']
    return max_order + 1 if max_order else 1


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        try:
            return ProductCategory.objects.filter(store=self.request.user.store)
        except Store.DoesNotExist:
            return ProductCategory.objects.none()

    @action(detail=True, methods=['post'])
    def move(self, request, uuid=None):
        category = get_object_or_404(ProductCategory, uuid=uuid)
        serializer = MoveProductCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        position = serializer.data.get("position")

        with transaction.atomic():
            siblings = list(ProductCategory.objects.filter(
                store=request.user.store).exclude(
                pk=category.pk).order_by("order"))

            siblings.insert(position - 1, category)

            for i, pc in enumerate(siblings, start=1):
                pc.order = i
                pc.save()

        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_new_product_order(self, store):
        results = Product.objects.filter(store=store).aggregate(Max('order'))
        max_order = results['order__max']
        return max_order + 1 if max_order else 1

    def get_new_category_order(self, store):
        results = ProductCategory.objects.filter(
            store=store).aggregate(Max('order'))
        max_order = results['order__max']
        return max_order + 1 if max_order else 1

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            store=self.request.user.store,
            order=self.get_new_product_order(self.request.user.store)
        )

    def get_queryset(self):
        try:
            return Product.objects.filter(store=self.request.user.store)
        except Store.DoesNotExist:
            return Product.objects.none()

    @action(detail=True, methods=['get'])
    def customers(self, request, uuid):
        """

        :param request:
        :param uuid:
        :return:
        """
        product = get_object_or_404(
            Product, store=request.user.store, uuid=uuid)

        customers = Customer.objects.filter(store=request.user.store,
                                            sale__product=product)

        return Response(CustomerSerializer(customers, many=True).data)

    @action(detail=True, methods=['post'])
    def add_category(self, request, uuid):
        """

        :param request:
        :param uuid:
        :return:
        """
        product = get_object_or_404(
            Product, store=request.user.store, uuid=uuid)

        serializer = ProductCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.data.get("name")

        try:
            pc = ProductCategory.objects.get(store=request.user.store,
                                             name=name)
        except ProductCategory.DoesNotExist:
            pc = ProductCategory.objects.create(
                store=request.user.store,
                name=name,
                order=self.get_new_category_order(request.user.store))

        product.categories.add(pc)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def delete_category(self, request, uuid):
        """

        :param request:
        :param uuid:
        :return:
        """
        product = get_object_or_404(
            Product, store=request.user.store, uuid=uuid)

        serializer = ProductCategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.data.get("name")

        try:
            pc = ProductCategory.objects.get(store=request.user.store,
                                             name=name)
            product.categories.remove(pc)

        except ProductCategory.DoesNotExist:
            pass

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_product_to_bundle(self, request, uuid):
        """

        :return:
        """
        product = get_object_or_404(
            Product, store=request.user.store, uuid=uuid)

        serializer = AddProductToBundleSerializer(
            data=request.data,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        linked_product = Product.objects.get(
            store=request.user.store,
            uuid=serializer.data.get("product_uuid"))

        content_item = ContentItem.objects.create(
            product=product,
            content_type="product",
            title="Link to {0}".format(str(linked_product.uuid)),
            linked_product=linked_product,
            order=get_new_content_item_order(product, None)
        )

        return Response(ContentItemSerializer(content_item).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def move(self, request, uuid=None):
        product = get_object_or_404(Product, uuid=uuid)
        serializer = MoveProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        position = serializer.data.get("position")

        with transaction.atomic():
            siblings = list(Product.objects.filter(
                store=request.user.store).exclude(
                pk=product.pk).order_by("order"))

            siblings.insert(position - 1, product)

            for i, p in enumerate(siblings, start=1):
                p.order = i
                p.save()

        return Response(serializer.data)


class ContentItemViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = ContentItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"


    def perform_create(self, serializer):
        product_uuid = self.kwargs.get("product_uuid")
        product = get_object_or_404(Product, uuid=product_uuid)
        parent_uuid = serializer.initial_data.get("parent_uuid")
        parent_item = ContentItem.objects.get(uuid=parent_uuid) if parent_uuid else None
        file_name = serializer.initial_data.get("file_name")

        file_path = None
        presigned_url = None
        presigned_url_fields = None
        media_id = None

        # Generate presigned upload URL for S3
        if serializer.initial_data["content_type"] == "file":
            file_path = find_free_file_path(
                str(self.request.user.uuid),
                product_uuid,
                file_name
            )

            res = create_presigned_post(AWS_STORAGE_BUCKET_NAME,
                                              file_path)

            presigned_url = res["url"]
            presigned_url_fields = res["fields"]
        elif serializer.initial_data["content_type"] == "video":
            jwplatform_client = jwplatform.Client(JWPLAYER_KEY, JWPLAYER_SECRET)
            res = jwplatform_client.videos.create(
                title="{0}/{1}/{2}".format(
                    str(self.request.user.uuid), product_uuid, file_name))

            presigned_url = 'https://{}{}'.format(
                res['link']['address'],
                res['link']['path']
            )
            presigned_url_fields = res['link']['query']
            presigned_url_fields['api_format'] = "json"

            media_id = res["media"]["key"]

        serializer.save(product=product,
                        parent_item=parent_item,
                        file_path=file_path,
                        presigned_url=presigned_url,
                        presigned_url_fields=presigned_url_fields,
                        media_id=media_id,
                        order=get_new_content_item_order(product, parent_item))

    def get_queryset(self):
        product_uuid = self.kwargs.get("product_uuid")
        product = get_object_or_404(Product, uuid=product_uuid)

        if self.request.method == 'GET':
            return ContentItem.objects.filter(
                product=product, parent_item=None).order_by("order")

        return ContentItem.objects.filter(
            product=product).order_by("order")


    @action(detail=True, methods=['post'])
    def move(self, request, uuid=None, product_uuid=None):
        product = get_object_or_404(Product, uuid=product_uuid)
        item = get_object_or_404(ContentItem, uuid=uuid)
        old_parent = item.parent_item

        serializer = MoveContentItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent_uuid = serializer.data.get("parent_uuid")
        position = serializer.data.get("position")
        new_parent = get_object_or_404(ContentItem, uuid=parent_uuid) \
            if parent_uuid else None

        with transaction.atomic():
            item.parent_item = new_parent
            item.save()

            siblings = list(ContentItem.objects.filter(
                product=product, parent_item=new_parent).exclude(
                pk=item.pk).order_by("order"))

            siblings.insert(position-1, item)

            for i, content_item in enumerate(siblings, start=1):
                content_item.order = i
                content_item.save()

            if item.parent_item != old_parent:
                prev_siblings = list(ContentItem.objects.filter(
                    product=product, parent_item=old_parent).order_by("order"))

                for i, content_item in enumerate(prev_siblings, start=1):
                    content_item.order = i
                    content_item.save()

        return Response(serializer.data)
