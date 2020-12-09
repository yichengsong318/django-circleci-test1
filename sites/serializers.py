from rest_framework import serializers
from sites.models import Page


class PageSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = Page
        fields = [
            "uuid",
            "slug",
            "title",
            "content",
            "schema",
            "schema_draft",
            "published",
            "created_at",
            "updated_at"
        ]


class BuilderPreviewSerializer(serializers.Serializer):
    """

    """
    type = serializers.CharField()
    title = serializers.CharField()
    uuid = serializers.UUIDField()


class AddSectionToDraftSchemaSerializer(serializers.Serializer):
    """

    """
    type = serializers.CharField()
    uuid = serializers.UUIDField()
    section_type = serializers.CharField()


class UpdateSectionInDraftSchemaSerializer(serializers.Serializer):
    """

    """
    type = serializers.CharField()
    uuid = serializers.UUIDField()
    section = serializers.JSONField()


class MoveSectionInDraftSchemaSerializer(serializers.Serializer):
    """

    """
    type = serializers.CharField()
    uuid = serializers.UUIDField()
    source_index = serializers.IntegerField()
    destination_index = serializers.IntegerField()