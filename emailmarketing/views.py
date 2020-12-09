import pytz
from django.contrib.auth import get_user_model
from django.shortcuts import (
    get_object_or_404
)
from rest_framework.views import APIView
from rest_framework import (
    generics,
    status,
    viewsets,
    permissions
)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from core.serializers import (
    UserSerializer,
    UserUpdateSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    NotificationSettingsSerializer,
    StoreSerializer,
    TimezoneSerializer
)
from core.models import (
    NotificationSettings,
    Store
)

from emailmarketing.serializers import (
    EmailMarketingSettingsSerializer
)
from emailmarketing.models import (
    EmailMarketingSettings
)


class EmailMarketingSettingsView(APIView):
    """

    """
    http_method_names = ["get", "put"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :return:
        """
        settings = get_object_or_404(
            EmailMarketingSettings, store=request.user.store)

        return Response(EmailMarketingSettingsSerializer(settings).data)

    def put(self, request):
        """

        :param request:
        :return:
        """
        settings = get_object_or_404(
            EmailMarketingSettings, store=request.user.store)

        serializer = EmailMarketingSettingsSerializer(
            settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
