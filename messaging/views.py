from django.shortcuts import (
    render,
    get_object_or_404
)
from rest_framework import (
    generics,
    status,
    viewsets,
    permissions
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt import tokens
from rest_framework.views import APIView

from messaging.models import (
    MessagingSettings,
    Chat
)


from messaging.serializers import (
    MessagingSettingsSerializer,
    ChatSerializer,
    MessageSerializer
)


class MessagingSettingsView(APIView):
    """

    """
    http_method_names = ["get", "put"]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return:
        """
        settings = get_object_or_404(MessagingSettings,
                                     store=request.user.store)

        return Response(MessagingSettingsSerializer(settings).data)

    def put(self, request):
        """

        :return:
        """
        settings = get_object_or_404(MessagingSettings,
                                     store=request.user.store)

        serializer = MessagingSettingsSerializer(settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ChatViewSet(viewsets.ModelViewSet):
    """

    """
    serializer_class = ChatSerializer
    http_method_names = ["get"]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "uuid"

    def get_queryset(self):
        try:
            return Chat.objects.filter(store=self.request.user.store)
        except Chat.DoesNotExist:
            return Chat.objects.none()

    @action(detail=True, methods=["get"])
    def messages(self, request, uuid):
        """

        :param request:
        :param chat_uuid:
        :return:
        """
        chat = get_object_or_404(Chat, uuid=uuid)
        return Response(MessageSerializer(chat.messages, many=True).data)