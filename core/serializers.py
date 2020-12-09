import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import (
    NotificationSettings,
    Store,
    SupportedCurrency,
    UploadedImage,
    UploadedVideo
)
from saas_template.settings import APP_DOMAIN


class UserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    is_store_owner = serializers.ReadOnlyField()

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords must match.')
        return data

    def create(self, validated_data):
        data = {
            key: value for key, value in validated_data.items()
            if key not in ('password1', 'password2')
        }
        data['username'] = str(uuid.uuid4())
        data['password'] = validated_data['password1']
        user = self.Meta.model.objects.create_user(**data)
        user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = (
            'uuid',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'is_store_owner'
        )

class UserUpdateSerializer(serializers.ModelSerializer):
    """

    """
    uuid = serializers.UUIDField(required=False, read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = (
            "uuid",
            "first_name",
            "last_name",
            "email"
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    store_slug = serializers.SlugField(allow_null=True)

    default_error_messages = {
        'no_active_account': 'No active account found with the given credentials'
    }

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)


    def validate(self, attrs):
        user_model = get_user_model()

        email = attrs["email"]
        password = attrs["password"]

        try:
            store_slug = attrs["store_slug"]
        except KeyError:
            store_slug = None

        user = None
        try:
            if store_slug:
                user = user_model.objects.get(
                    email=email,
                    customer_of__store_slug=store_slug)
            else:
                user = user_model.objects.get(email=email, customer_of=None)
        except user_model.DoesNotExist:
            pass

        if (user is None or
                not user.is_active or
                not user.check_password(password)):
            raise AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }


class ChangePasswordSerializer(serializers.Serializer):
    """

    """
    BAD_PASSWORD_MSG = "Your password is incorrect."
    DO_NOT_MATCH_MSG = "Your new passwords do not match."

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, old_password):
        user = self.context["request"].user
        if not user.check_password(old_password):
            raise serializers.ValidationError(self.BAD_PASSWORD_MSG)

        return old_password

    def validate_new_password(self, new_password):
        try:
            validate_password(new_password)
        except ValidationError as ve:
            raise serializers.ValidationError(' '.join(ve.messages))

        return new_password

    def validate(self, attrs):
        """

        :param attrs:
        :return:
        """
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                "new_password_confirm": self.DO_NOT_MATCH_MSG
            })

        return attrs


class NotificationSettingsSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)

    class Meta:
        model = NotificationSettings
        fields = [
            "uuid",
            "new_free_product_email",
            "new_sale_email",
            "new_membership_email",
            "cancel_membership_email",
            "new_message_email",
            "new_message_app",
            "course_comment_email",
            "course_completed_email"
        ]

class StoreSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)
    store_url = serializers.SerializerMethodField(read_only=True)
    currency_info = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_store_url(self, obj):
        if obj.subdomain:
            return "https://{0}".format(obj.subdomain)

        return "https://{0}.{1}".format(obj.store_slug, APP_DOMAIN)

    def get_currency_info(self, obj):
        if obj.currency is None:
            return None

        if SupportedCurrency.objects.filter(code=obj.currency):
            currency = SupportedCurrency.objects.get(code=obj.currency)
            return SupportedCurrencySerializer(currency).data

    class Meta:
        model = Store
        fields = [
            "uuid",
            "name",
            "store_slug",
            "store_url",
            "currency",
            "currency_info",
            "tax_address",
            "collect_tax_addresses",
            "timezone",
            "language",
            "subdomain",
            "custom_domain",
            "schema",
            "schema_draft",
            "product_section_layout",
            "category_section_layout",
            "created_at",
            "updated_at"
        ]


class TimezoneSerializer(serializers.Serializer):
    tz_value = serializers.SerializerMethodField()
    tz_name = serializers.SerializerMethodField()

    def get_tz_value(self, obj):
        return obj

    def get_tz_name(self, obj):
        return obj


class SupportedCurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportedCurrency
        fields = [
            "code",
            "symbol",
            "name",
            "multiple",
            "order"
        ]


class UploadedImageSlimSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)
    url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_url(self, obj):
        """

        :param obj:
        :return:
        """
        return obj.url

    class Meta:
        model = UploadedImage
        fields = [
            "uuid",
            "name",
            "url",
            "created_at",
            "updated_at"
        ]


class UploadedVideoSlimSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False, read_only=True)
    player_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(required=False, read_only=True)
    updated_at = serializers.DateTimeField(required=False, read_only=True)

    def get_player_url(self, obj):
        return obj.player_url

    class Meta:
        model = UploadedVideo
        fields = [
            "uuid",
            "name",
            "presigned_url",
            "presigned_url_fields",
            "media_id",
            "player_url",
            "created_at",
            "updated_at"
        ]