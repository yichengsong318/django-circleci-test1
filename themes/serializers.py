from rest_framework import serializers
from themes.models import (
    SiteTheme,
    SiteThemeTemplate,
    SiteThemeSection,
    SiteThemeAsset,
    SiteThemeVariable
)


class SiteThemeVariableSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = SiteThemeVariable
        fields = [
            "uuid",
            "name",
            "value",
            "binary_value",
            "variable_type",
            "created_at",
            "updated_at"
        ]


class SiteThemeEntitySerializer(serializers.ModelSerializer):
    UNIQUE_NAME_MSG = 'Names must be unique.'

    def validate(self, attrs):
        theme = self.context['theme']
        name = attrs.get('name')

        try:
            existing = self.Meta.model.objects.get(site_theme=theme,
                                                     name=name)

        except self.Meta.model.DoesNotExist:
            return attrs

        if self.instance and self.instance.uuid == existing.uuid:
            return attrs
        else:
            raise serializers.ValidationError(
                {"name": self.UNIQUE_NAME_MSG})


class SiteThemeTemplateSlimSerializer(SiteThemeEntitySerializer):
    UNIQUE_NAME_MSG = 'Templates must have unique names.'

    uuid = serializers.UUIDField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = SiteThemeTemplate
        fields = [
            "uuid",
            "name",
            "template_type",
            "created_at",
            "updated_at"
        ]


class SiteThemeTemplateSerializer(SiteThemeTemplateSlimSerializer):
    """

    """
    class Meta:
        model = SiteThemeTemplate
        fields = [
            "uuid",
            "name",
            "template_type",
            "content",
            "created_at",
            "updated_at"
        ]


class SiteThemeSectionSlimSerializer(SiteThemeEntitySerializer):
    """

    """
    UNIQUE_NAME_MSG = 'Sections must have unique names.'

    uuid = serializers.UUIDField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = SiteThemeSection
        fields = [
            "uuid",
            "name",
            "section_type",
            "created_at",
            "updated_at"
        ]


class SiteThemeSectionSerializer(SiteThemeSectionSlimSerializer):
    """

    """
    class Meta:
        model = SiteThemeSection
        fields = [
            "uuid",
            "name",
            "section_type",
            "content",
            "created_at",
            "updated_at"
        ]


class SiteThemeAssetSlimSerializer(SiteThemeEntitySerializer):
    """

    """
    UNIQUE_NAME_MSG = 'Assets must have unique names.'

    uuid = serializers.UUIDField(required=False, read_only=True)
    editable = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_editable(self, obj):
        return obj.editable

    class Meta:
        model = SiteThemeAsset
        fields = [
            "uuid",
            "name",
            "asset_type",
            "editable",
            "created_at",
            "updated_at"
        ]


class SiteThemeAssetSerializer(SiteThemeAssetSlimSerializer):
    """

    """
    class Meta:
        model = SiteThemeAsset
        fields = [
            "uuid",
            "name",
            "asset_type",
            "content",
            "editable",
            "created_at",
            "updated_at"
        ]


class SiteThemeSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)
    variables = SiteThemeVariableSerializer(source="sitethemevariable_set",
                                            many=True, read_only=True)
    templates = SiteThemeTemplateSlimSerializer(source="sitethemetemplate_set",
                                            many=True, read_only=True)
    sections = SiteThemeSectionSlimSerializer(source="sitethemesection_set",
                                          many=True, read_only=True)
    assets = SiteThemeAssetSlimSerializer(source="sitethemeasset_set",
                                          many=True, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = SiteTheme
        fields = [
            "uuid",
            "name",
            "live",
            "variables",
            "templates",
            "sections",
            "assets",
            "created_at",
            "updated_at"
        ]


class TemplateTypeSerializer(serializers.Serializer):
    """

    """
    code = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)


class SectionTypeSerializer(serializers.Serializer):
    """

    """
    code = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)


class AssetTypeSerializer(serializers.Serializer):
    """

    """
    code = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
