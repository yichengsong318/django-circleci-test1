from rest_framework import serializers
from emailmarketing.models import (
    EmailMarketingSettings
)


class EmailMarketingSettingsSerializer(serializers.ModelSerializer):
    """

    """
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = EmailMarketingSettings
        fields = [
            "mailing_address",
            "double_opt_in",
            "opt_in_text",
            "created_at",
            "updated_at"
        ]
