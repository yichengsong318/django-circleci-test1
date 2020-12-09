import pytz
import uuid
import jwplatform
from django.contrib.auth import get_user_model
from django.shortcuts import (
    get_object_or_404
)
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import (
    generics,
    status,
    viewsets,
    permissions
)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserSerializer,
    UserUpdateSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    NotificationSettingsSerializer,
    StoreSerializer,
    TimezoneSerializer,
    SupportedCurrencySerializer,
    UploadedImageSlimSerializer,
    UploadedVideoSlimSerializer
)
from core.models import (
    NotificationSettings,
    Store,
    SupportedCurrency,
    UploadedImage,
    UploadedVideo
)
from saas_template.settings import (
    JWPLAYER_KEY,
    JWPLAYER_SECRET
)


class RegistrationView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    http_method_names = ["post"]

    def post(self, request, **kwargs):
        user = self.request.user
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.data.get("new_password"))
        user.save()

        return Response(data={"message": "password changed"},
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserUpdateSerializer
    http_method_names = ["get", "put"]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        try:
            return get_user_model().objects.filter(id=self.request.user.id)
        except get_user_model().DoesNotExist:
            return get_user_model().objects.none()


class NotificationSettingsView(APIView):
    """

    """
    http_method_names = ["get", "put"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :return:
        """
        notifications = get_object_or_404(
            NotificationSettings, store=request.user.store)

        return Response(NotificationSettingsSerializer(notifications).data)

    def put(self, request):
        """

        :param request:
        :return:
        """
        notifications = get_object_or_404(
            NotificationSettings, store=request.user.store)

        serializer = NotificationSettingsSerializer(
            notifications, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

class StoreView(APIView):
    """

    """
    http_method_names = ["get", "put"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return:
        """
        store = get_object_or_404(Store, owner=request.user)
        return Response(StoreSerializer(store).data)

    def put(self, request):
        """

        :param request:
        :return:
        """
        store = get_object_or_404(Store, owner=request.user)

        serializer = StoreSerializer(store, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class UploadedImageViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = UploadedImageSlimSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def perform_create(self, serializer):
        serializer.save(store=self.request.user.store)

    def get_queryset(self):
        return UploadedImage.objects.filter(store=self.request.user.store)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        name= request.data.get("name")
        file = request.data.get("file")
        image = UploadedImage.objects.create(
            store=request.user.store,
            name=name,
            content=file.read())

        return Response(UploadedImageSlimSerializer(image).data,
                        status=status.HTTP_201_CREATED)


class UploadedVideoViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = UploadedVideoSlimSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def perform_create(self, serializer):
        name = serializer.initial_data.get("name")
        jwplatform_client = jwplatform.Client(JWPLAYER_KEY, JWPLAYER_SECRET)
        res = jwplatform_client.videos.create(
            title="{0}/{1}/{2}".format(
                str(self.request.user.uuid), str(uuid.uuid4()), name))

        presigned_url = 'https://{}{}'.format(
            res['link']['address'],
            res['link']['path']
        )
        presigned_url_fields = res['link']['query']
        presigned_url_fields['api_format'] = "json"

        media_id = res["media"]["key"]


        serializer.save(
            store=self.request.user.store,
            presigned_url=presigned_url,
            presigned_url_fields=presigned_url_fields,
            media_id=media_id,
        )

    def get_queryset(self):
        return UploadedVideo.objects.filter(store=self.request.user.store)


class TimezoneView(APIView):
    """

    """
    serializer_class = UploadedVideoSlimSerializer
    http_method_names = ["get"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            TimezoneSerializer(pytz.common_timezones, many=True).data)


class SupportedCurrencyView(APIView):
    http_method_names = ["get"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(SupportedCurrencySerializer(
            SupportedCurrency.objects.all(), many=True).data)