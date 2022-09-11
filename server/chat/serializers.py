from rest_framework import serializers

# from users.models import User
from .models import Message, Room

from users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = Message
        exclude = []
        depth = 1

    def get_created_at_formatted(self, obj: Message):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    current_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ["pk", "messages", "current_users", "last_message", 'name']
        depth = 1
        read_only_fields = ["messages", "last_message"]

    def get_last_message(self, obj: Room):
        return MessageSerializer(obj.messages.order_by('created_at').last()).data


class RoomNotifySerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ["pk", 'name']


class RoomChatSerializer(serializers.ModelSerializer):
    # last_message = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    current_users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ["pk", "messages", "current_users", 'room_type', 'name']
        depth = 1
        read_only_fields = ["messages"]

    # def get_last_message(self, obj: Room):
    #     return MessageSerializer(obj.messages.order_by('-created_at').first()).data

    def get_messages(self, obj: Room):
        return MessageChatSerializer(obj.messages.order_by('-created_at')[:2], many=True).data


class MessageChatSerializer(serializers.ModelSerializer):

    created_at_formatted = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = Message
        fields = ['id', 'user', 'text', 'created_at_formatted']

    def get_created_at_formatted(self, obj: Message):
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")
