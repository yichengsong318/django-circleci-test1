from rest_framework import serializers

from payments.models import StripeConnect
from payments.utils import get_connect_url


class StripeConnectSerializer(serializers.ModelSerializer):
    """

    """
    connected = serializers.SerializerMethodField()
    authorization_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_connected(self, obj):
        return obj.connected_account_id is not None

    def get_authorization_url(self, obj):
        if obj.connected_account_id is None:
            return get_connect_url(
                obj.redirect_state,
                obj.scope,
                obj.store.owner.email
            )

        return None

    class Meta:
        model = StripeConnect
        fields = [
            "redirect_state",
            "scope",
            "connected",
            "authorization_url",
            "created_at",
            "updated_at"
        ]
