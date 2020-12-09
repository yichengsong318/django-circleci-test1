import json
from uuid import UUID

from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from core.models import User
from messaging.models import (
    Chat,
    Message
)
from messaging.serializers import (
    ChatWebsocketSerializer,
    MessageWebsocketSerializer
)

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class MessagingConsumer(JsonWebsocketConsumer):

    def send_json(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        super().send(
            text_data=json.dumps(content, cls=UUIDEncoder), close=close)

    def message_create(self, content):
        user = self.scope["user"]

        if user.customer_of is None:
            sender = 'STORE'
            store = user.store
            customer = User.objects.get(uuid=content.get("recipient_uuid"))
        else:
            sender = 'USER'
            store = user.customer_of
            customer = user

        if Chat.objects.filter(store=store, user=customer).exists():
            chat = Chat.objects.get(store=store, user=customer)
        else:
            chat = Chat.objects.create(store=store, user=customer)

        message = Message.objects.create(
            chat=chat,
            sender=sender,
            message=content.get("message")
        )

        data = {
            "chat": ChatWebsocketSerializer(chat).data,
            "message": MessageWebsocketSerializer(message).data
        }

        if sender == "STORE":
            print("sending to user group")
            print(customer.uuid)
            async_to_sync(self.channel_layer.group_send)(
                group=str(customer.uuid),
                message={
                    "type": "message.receive",
                    "data": data
                })
        else:
            async_to_sync(self.channel_layer.group_send)(
                group=str(store.uuid),
                message={
                    "type": "message.receive",
                    "data": data
                })

        self.send_json({
            "type": "message.echo",
            "data": data
        })

    def message_receive(self, content):
        self.send_json(content)

    def message_echo(self, content):
        self.send_json(content)

    def message_acknowledge(self, content):
        pass

    def update_status(self, content):
        pass

    def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            self.close()

        print("USER:")
        print(user)
        print(user.uuid)
        if user.customer_of is None:
            async_to_sync(self.channel_layer.group_add)(group=str(user.store.uuid),
                                         channel=self.channel_name)
        else:
            print("customer UUID:")
            print(user.uuid)
            async_to_sync(self.channel_layer.group_add)(group=str(user.uuid),
                                         channel=self.channel_name)

        self.accept()

    def disconnect(self, code):
        user = self.scope["user"]

        if hasattr(user, "store"):
            async_to_sync(self.channel_layer.group_discard)(group=str(user.store.uuid),
                                             channel=self.channel_name)
        else:
            async_to_sync(self.channel_layer.group_discard)(group=str(user.uuid),
                                             channel=self.channel_name)

        super().disconnect(code)


    def receive_json(self, content, **kwargs):
        message_type = content.get("type")

        print(message_type)

        if message_type == "message.create":
            self.message_create(content)
        elif message_type == "message.receive":
            self.message_receive(content)
        elif message_type == "message.echo":
            self.message_echo(content)
        elif message_type == "message.acknowledge":
            self.message_acknowledge(content)
        elif message_type == "status.update":
            self.update_status(content)
