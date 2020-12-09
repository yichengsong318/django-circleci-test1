from rest_framework import serializers
from customers.models import (
    Customer,
    Sale,
    MembershipSubscription
)
from products.serializers import (
    ProductSerializer,
    MembershipSerializer
)
from core.serializers import UserSerializer


class CustomerSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)
    user = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)


    class Meta:
        model = Customer
        fields = [
            "uuid",
            "email",
            "user",
            "created_at",
            "updated_at"
        ]


class SaleSerializer(serializers.ModelSerializer):
    """

    """
    uuid = serializers.UUIDField(required=False, read_only=True)
    customer = CustomerSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "uuid",
            "customer",
            "product",
            "created_at",
            "updated_at"
        ]


class MembershipSubscriptionSerializer(serializers.ModelSerializer):
    """

    """
    uuid = serializers.UUIDField(required=False, read_only=True)
    customer = CustomerSerializer(read_only=True)
    membership = MembershipSerializer(read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = MembershipSubscription
        fields = [
            "uuid",
            "customer",
            "membership",
            "valid_until",
            "stripe_subscription_id",
            "stripe_product_id",
            "stripe_subscription_status",
            "latest_invoice_payment_intent_status",
            "created_at",
            "updated_at"
        ]