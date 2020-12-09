from rest_framework import serializers

from messaging.models import (
    MessagingSettings,
    Chat,
    Message
)
from core.serializers import UserSerializer


class MessagingSettingsSerializer(serializers.ModelSerializer):
    """

    """
    DISPLAY_NAME_NEEDED_MSG = "You must enter a display name."

    uuid = serializers.UUIDField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def validate(self, attrs):
        chat_display_as = attrs.get("chat_display_as")
        chat_display_name = attrs.get("chat_display_name")

        if chat_display_as == "CUSTOM" and chat_display_name is None:
            raise serializers.ValidationError({
                "chat_display_name": self.DISPLAY_NAME_NEEDED_MSG})

        return attrs

    class Meta:
        model = MessagingSettings
        fields = [
            "uuid",
            "chat_display_as",
            "chat_display_name",
            "default_status",
            "chat_available_to",
            "play_sounds",
            "created_at",
            "updated_at"
        ]


class ChatSerializer(serializers.ModelSerializer):
    """

    """
    uuid = serializers.UUIDField(required=False, read_only=True)
    user = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = Chat
        fields = [
            "uuid",
            "user",
            "created_at",
            "updated_at"
        ]

class ChatWebsocketSerializer(serializers.ModelSerializer):
    """

    """
    uuid = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_uuid(self, obj):
        return str(obj.uuid)

    def get_user_uuid(self, obj):
        return str(obj.user.uuid)

    class Meta:
        model = Chat
        fields = [
            "uuid",
            "user",
            "created_at",
            "updated_at"
        ]


class MessageSerializer(serializers.ModelSerializer):
    """

    """
    uuid = serializers.UUIDField(required=False, read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = Message
        fields = [
            "uuid",
            "sender",
            "message",
            "seen",
            "acknowledged",
            "created_at",
            "updated_at"
        ]


class MessageWebsocketSerializer(serializers.ModelSerializer):
    uuid = serializers.SerializerMethodField()
    chat_uuid = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_uuid(self, obj):
        return str(obj.uuid)

    def get_chat_uuid(self, obj):
        return str(obj.chat.uuid)

    class Meta:
        model = Message
        fields = [
            "uuid",
            "chat_uuid",
            "sender",
            "message",
            "seen",
            "acknowledged",
            "created_at",
            "updated_at"
        ]
