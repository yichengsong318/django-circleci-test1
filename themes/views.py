import base64
from django.shortcuts import get_object_or_404
from rest_framework import (
    status,
    viewsets,
    permissions
)
from rest_framework.decorators import action
from rest_framework.response import Response

from themes.models import (
    SiteTheme,
    SiteThemeVariable,
    SiteThemeTemplate,
    SiteThemeSection,
    SiteThemeAsset,
    TEMPLATE_TYPES,
    SECTION_TYPES,
    ASSET_TYPES
)

from themes.serializers import (
    SiteThemeSerializer,
    SiteThemeVariableSerializer,
    SiteThemeTemplateSerializer,
    SiteThemeSectionSerializer,
    SiteThemeAssetSerializer,
    SiteThemeAssetSlimSerializer,
    TemplateTypeSerializer,
    SectionTypeSerializer,
    AssetTypeSerializer
)


class SiteThemeViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = SiteThemeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        return SiteTheme.objects.filter(store=self.request.user.store)

    @action(detail=False, methods=['get'])
    def template_types(self, request):
        return Response(
            TemplateTypeSerializer(
                [{"code": t[0], "name": t[1]} for t in TEMPLATE_TYPES],
                many=True).data)

    @action(detail=False, methods=['get'])
    def section_types(self, request):
        return Response(
            SectionTypeSerializer(
                [{"code": t[0], "name": t[1]} for t in SECTION_TYPES],
                many=True).data)

    @action(detail=False, methods=['get'])
    def asset_types(self, request):
        return Response(
            AssetTypeSerializer(
                [{"code": t[0], "name": t[1]} for t in ASSET_TYPES],
                many=True).data)


class SiteThemeEntityViewSet(viewsets.ModelViewSet):
    """

    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def perform_create(self, serializer):
        theme = get_object_or_404(
            SiteTheme, uuid=self.kwargs.get("sitetheme_uuid"))

        serializer.save(site_theme=theme)

    def create(self, request, *args, **kwargs):
        theme = get_object_or_404(
            SiteTheme, uuid=self.kwargs.get("sitetheme_uuid"))

        serializer = self.get_serializer_class()(
            data=request.data,
            context=dict(self.get_serializer_context(), **{"theme": theme}))

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        theme = get_object_or_404(
            SiteTheme, uuid=self.kwargs.get("sitetheme_uuid"))

        serializer = self.get_serializer_class()(
            instance, data=request.data, partial=partial,
            context=dict(self.get_serializer_context(), **{"theme": theme}))

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class SiteThemeVariableViewSet(SiteThemeEntityViewSet):
    """

    """
    serializer_class = SiteThemeVariableSerializer

    def get_queryset(self):
        theme = get_object_or_404(
            SiteTheme, uuid=self.kwargs.get("sitetheme_uuid"))

        return SiteThemeVariable.objects.filter(site_theme=theme)


class SiteThemeTemplateViewSet(SiteThemeEntityViewSet):
    """

    """
    serializer_class = SiteThemeTemplateSerializer

    def get_queryset(self):
        theme = get_object_or_404(
            SiteTheme, uuid=self.kwargs.get("sitetheme_uuid"))

        return SiteThemeTemplate.objects.filter(site_theme=theme)


    @action(detail=True, methods=['put'])
    def rename(self, request, sitetheme_uuid, uuid):
        theme = get_object_or_404(SiteTheme, uuid=sitetheme_uuid)
        template = get_object_or_404(
            SiteThemeTemplate, sitetheme=theme, uuid=uuid)

        serializer = SiteThemeTemplateSerializer(
            template, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class SiteThemeSectionViewSet(SiteThemeEntityViewSet):
    """

    """
    serializer_class = SiteThemeSectionSerializer

    def get_queryset(self):
        theme = get_object_or_404(
            SiteTheme, uuid=self.kwargs.get("sitetheme_uuid"))

        return SiteThemeSection.objects.filter(site_theme=theme)


class SiteThemeAssetViewSet(SiteThemeEntityViewSet):
    """

    """
    serializer_class = SiteThemeAssetSerializer

    def get_queryset(self):
        theme = get_object_or_404(
            SiteTheme, uuid=self.kwargs.get("sitetheme_uuid"))

        return SiteThemeAsset.objects.filter(site_theme=theme)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        theme = get_object_or_404(
            SiteTheme, uuid=self.kwargs.get("sitetheme_uuid"))

        serializer = self.get_serializer_class()(
            instance, data=request.data, partial=partial,
            context=dict(self.get_serializer_context(), **{"theme": theme}))

        serializer.is_valid(raise_exception=True)

        if "content" in serializer.initial_data:
            decoded = base64.b64decode(serializer.initial_data["content"])
            serializer.save(content=decoded)
        else:
            serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def upload(self, request, sitetheme_uuid):
        theme = get_object_or_404(
            SiteTheme, uuid=sitetheme_uuid)

        name = request.data.get("name")
        file = request.data.get("file")

        if any([name is None, file is None]):
            return Response({
                "name": "This field is required.",
                "file": "This field is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        asset = SiteThemeAsset.objects.create(
            site_theme=theme,
            name=name,
            asset_type='OTHER',
            content=file.read(),
        )

        return Response(SiteThemeAssetSlimSerializer(asset).data)