from rest_framework import serializers
from discounts.models import (
    DiscountCode,
    DiscountCodeUsage
)
from customers.serializers import (
    SaleSerializer,
    MembershipSubscriptionSerializer
)


class DiscountCodeSerializer(serializers.ModelSerializer):
    """

    """
    NOT_UNIQUE_MSG = "An active discount code with this name already exists."
    INVALID_PCT_MSG = "A percentage discount must be between 0 and 100"

    uuid = serializers.UUIDField(required=False, read_only=True)
    formatted_reduction = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_formatted_reduction(self, obj):
        return obj.formatted_reduction

    def validate_code(self, code):
        request = self.context['request']
        if request.method == "POST":
            store = self.context['request'].user.store

            if DiscountCode.objects.filter(
                    store=store, code=code, active=True).exists():
                raise serializers.ValidationError(self.NOT_UNIQUE_MSG)

        return code

    def validate(self, attrs):
        request = self.context['request']
        if request.method == "POST":
            reduction_type = attrs.get("reduction_type")
            reduction = attrs.get("reduction")

            if reduction_type == "percent" and reduction > 100:
                raise serializers.ValidationError({
                    "reduction": self.INVALID_PCT_MSG
                })

        return attrs


    class Meta:
        model = DiscountCode
        fields = [
            "uuid",
            "code",
            "reduction_type",
            "reduction",
            "formatted_reduction",
            "active",
            "expiry",
            "max_usages",
            "created_at",
            "updated_at"
        ]


class DiscountCodeUsageSerializer(serializers.ModelSerializer):
    """

    """
    uuid = serializers.UUIDField(required=False, read_only=True)
    discount_code = DiscountCodeSerializer(read_only=True)
    sale = SaleSerializer(read_only=True)
    subscription = MembershipSubscriptionSerializer(read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    class Meta:
        model = DiscountCodeUsage
        fields = [
            "uuid",
            "discount_code",
            "sale",
            "subscription",
            "created_at",
            "updated_at"
        ]
