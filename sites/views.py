import uuid
from django.db import transaction
from django.shortcuts import (
    render,
    get_object_or_404
)
from rest_framework import (
    views,
    viewsets,
    permissions,
    status
)
from rest_framework.response import Response

# Create your views here.
from sites.models import Page
from sites.serializers import (
    PageSerializer,
    BuilderPreviewSerializer,
    AddSectionToDraftSchemaSerializer,
    UpdateSectionInDraftSchemaSerializer,
    MoveSectionInDraftSchemaSerializer
)


from themes.models import (
    SiteTheme,
    SiteThemeTemplate
)

from products.models import (
    Product
)

from sites.renderutils import (
    render
)

from sites.utils import (
    build_page_section
)

class PublishChangesAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """

        :param request:
        :return:
        """
        store = request.user.store

        with transaction.atomic():
            store.schema = store.schema_draft
            store.save()

            for page in store.page_set.all():
                page.schema = page.schema_draft
                page.save()

            for product in store.product_set.filter(draft=False):
                product.schema = product.schema_draft
                product.save()

        return Response(status=status.HTTP_200_OK)


class AddSectionToDraftSchemaAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """

        :param request:
        :return:
        """
        store = request.user.store
        serializer = AddSectionToDraftSchemaSerializer(request.data)
        section = build_page_section(serializer.data["section_type"])

        if serializer.data["type"] == "home":
            store.schema_draft.append(section)
            store.save()
        elif serializer.data["type"] == "page":
            page = get_object_or_404(
                Page, store=store, uuid=serializer.data["uuid"])
            page.schema_draft.append(section)
            page.save()
        elif serializer.data["type"] == "product":
            product = get_object_or_404(
                Product, store=store, uuid=serializer.data["uuid"])
            product.schema_draft.append(section)
            product.save()

        return Response(section, status=status.HTTP_201_CREATED)


class UpdateSectionInDraftSchemaAPIView(views.APIView):
    """

    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """

        :param request:
        :return:
        """
        store = request.user.store
        serializer = UpdateSectionInDraftSchemaSerializer(request.data)
        updated = serializer.data["section"]

        if serializer.data["type"] == "home":
            obj = store
        elif serializer.data["type"] == "page":
            obj = get_object_or_404(
                Page, store=store, uuid=serializer.data["uuid"])
        elif serializer.data["type"] == "product":
            obj = get_object_or_404(
                Product, store=store, uuid=serializer.data["uuid"])
        else:
            obj = None

        if obj:
            idx = next(i for i, v in enumerate(obj.schema_draft)
                       if v["data_section_uuid"] == updated["data_section_uuid"])
            obj.schema_draft[idx] = updated
            obj.save()

        return Response(updated)


class DeleteSectionFromDraftSchemaAPIView(views.APIView):
    """

    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """

        :param request:
        :return:
        """
        store = request.user.store
        serializer = UpdateSectionInDraftSchemaSerializer(request.data)
        deleted = serializer.data["section"]

        if serializer.data["type"] == "home":
            obj = store
        elif serializer.data["type"] == "page":
            obj = get_object_or_404(
                Page, store=store, uuid=serializer.data["uuid"])
        elif serializer.data["type"] == "product":
            obj = get_object_or_404(
                Product, store=store, uuid=serializer.data["uuid"])
        else:
            obj = None

        if obj:
            idx = next(i for i, v in enumerate(obj.schema_draft)
                       if v["data_section_uuid"] == deleted["data_section_uuid"])
            obj.schema_draft.pop(idx)
            obj.save()

        return Response(deleted)


class MoveSectionInDraftSchemaAPIView(views.APIView):
    """

    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """

        :param request:
        :return:
        """
        store = request.user.store
        serializer = MoveSectionInDraftSchemaSerializer(request.data)

        if serializer.data["type"] == "home":
            obj = store
        elif serializer.data["type"] == "page":
            obj = get_object_or_404(
                Page, store=store, uuid=serializer.data["uuid"])
        elif serializer.data["type"] == "product":
            obj = get_object_or_404(
                Product, store=store, uuid=serializer.data["uuid"])
        else:
            obj = None

        if obj:
            obj.schema_draft.insert(
                serializer.data["destination_index"],
                obj.schema_draft.pop(serializer.data["source_index"]))
            obj.save()

        return Response(obj.schema_draft)


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return Page.objects.filter(store=self.request.user.store)


class BuilderPreviewAPIView(views.APIView):
    """

    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """

        :param request:
        :return:
        """
        store = request.user.store
        active_theme = get_object_or_404(SiteTheme,
                                         store=store, live=True)

        serializer = BuilderPreviewSerializer(request.data)

        if serializer.data["type"] == "home":
            template = get_object_or_404(
                SiteThemeTemplate,
                site_theme=active_theme,
                template_type="INDEX")

            src = render(template, context={
                "user": request.user,
                "store": store,
                "theme": active_theme,
                "sections": store.schema_draft
            })

        elif serializer.data["type"] == "page":
            page = get_object_or_404(
                Page, store=store, uuid=serializer.data["uuid"])
            template = get_object_or_404(
                SiteThemeTemplate,
                site_theme=active_theme,
                template_type="PAGE")

            src = render(template, context={
                "user": request.user,
                "store": store,
                "page": page,
                "theme": active_theme,
                "sections": page.schema_draft
            })

        elif serializer.data["type"] == "product":
            product = get_object_or_404(
                Product, store=store, uuid=serializer.data["uuid"])
            template = get_object_or_404(
                SiteThemeTemplate,
                site_theme=active_theme,
                template_type="PRODUCT")

            src = render(template, context={
                "user": request.user,
                "store": store,
                "product": product,
                "theme": active_theme,
                "sections": product.schema_draft
            })

        # print(src)
        return Response({
            "src": src
        })
