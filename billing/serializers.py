from rest_framework import serializers
from billing.models import (
    StripeCustomer,
    StripeSubscription
)

class StripeBillingPortalSerializer(serializers.Serializer):
    """

    """
    id = serializers.CharField()
    object = serializers.CharField()
    created = serializers.IntegerField()
    customer = serializers.CharField()
    return_url = serializers.URLField()
    url = serializers.URLField()


class StripeSubscriptionSerializer(serializers.ModelSerializer):
    """

    """
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = StripeSubscription
        fields = [
            "stripe_subscription_id",
            "stripe_product_id",
            "plan",
            "status",
            "latest_invoice_payment_intent_status",
            "created_at",
            "updated_at"
        ]


class StripeCustomerSerializer(serializers.ModelSerializer):
    subscription = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_subscription(self, obj):
        subscription = obj.subscription

        if subscription is None:
            return None

        return StripeSubscriptionSerializer(subscription).data


    class Meta:
        model = StripeCustomer
        fields = [
            "stripe_customer_id",
            "stripe_payment_method_id",
            "subscription",
            "created_at",
            "updated_at"
        ]