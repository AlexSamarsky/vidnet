import json

# from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
# from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer.generics import (
    ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer

from .models import Room, Message, UnreadMessage
from users.models import User
from .serializers import MessageSerializer, RoomSerializer, UserSerializer


class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"

    async def disconnect(self, code):
        if hasattr(self, "room_subscribe"):
            # await self.remove_user_from_room(self.room_subscribe)
            self.room_subscribe = None
            await self.notify_users()
        await super().disconnect(code)

    @action()
    async def join_private_room(self, user_pk, **kwargs):
        obj = {
            'user_pk': user_pk,
            'scope_user_pk': self.scope["user"].id
        }
        room: Room = await self.get_private_room(user_pk)
        obj['room'] = room.id

        self.room_subscribe = room.id
        self.room_user_id = self.scope["user"].id
        await self.message_activity.subscribe(room=room.id)
        # await self.notify_users()
        return obj, 200

    @action()
    async def join_public_room(self, room_pk, user_pk, **kwargs):
        obj = {
            'scope_user_pk': self.scope["user"].id
        }
        room: Room = await self.get_private_room(user_pk)
        obj['room'] = room.id

        self.room_subscribe = room.id
        self.room_user_id = self.scope["user"].id
        await self.message_activity.subscribe(room=room.id)
        # await self.notify_users()
        return obj, 200

    @action()
    async def create_message(self, message, **kwargs):
        room: Room = await self.get_room(room_pk=self.room_subscribe)
        await database_sync_to_async(Message.objects.create)(
            room=room,
            user=self.scope["user"],
            text=message
        )
        # await self.apply_unread_message(message_obj)

    @action()
    async def action_add_user_to_room(self, room_pk, user_pk, **kwargs):
        try:
            room = await self.add_user_to_room(room_pk, user_pk)
            return room, 200
        except (Room.DoesNotExist, User.DoesNotExist) as error:
            return {"error": error}, 404

    @action()
    async def action_remove_user_from_room(self, room_pk, user_pk, **kwargs):
        try:
            room = await self.remove_user_from_room(room_pk, user_pk)
            return room, 200
        except (Room.DoesNotExist, User.DoesNotExist) as error:
            return {"error": error}, 404

    @action()
    async def action_create_public_room(self, name, **kwargs):
        room = await self.create_room_for_user(name)

        return room, 200

    @action()
    async def subscribe_to_messages_in_room(self, room_pk, **kwargs):
        room = await self.get_room(room_pk=room_pk, user_pk=self.scope['user'].id)
        if not room:
            return {"error": "illegible room"}, 404

        self.room_subscribe = room_pk
        self.room_user_id = self.scope["user"].id
        await self.message_activity.subscribe(room=room_pk)

        return {"success": "ok"}, 200

    @model_observer(Message)
    async def message_activity(self, message, observer=None, **kwargs):
        if not message['data']['user']['id'] == self.room_user_id:
            await self.move_unread_message()
        await self.send_json(message)

    @message_activity.groups_for_signal
    def message_activity(self, instance: Message, **kwargs):
        yield f'room__{instance.room_id}'
        yield f'pk__{instance.pk}'

    @message_activity.groups_for_consumer
    def message_activity(self, room=None, **kwargs):
        if room is not None:
            yield f'room__{room}'

    @message_activity.serializer
    def message_activity(self, instance: Message, action, **kwargs):
        return dict(data=MessageSerializer(instance).data, action=action.value, pk=instance.pk)

    async def notify_users(self):
        room: Room = await self.get_room(pk_room=self.room_subscribe)
        if self.groups:
            for group in self.groups:
                await self.channel_layer.group_send(
                    group,
                    {
                        'type': 'update_users',
                        'usuarios': await self.current_users(room)
                    }
                )

    async def update_users(self, event: dict):
        await self.send(text_data=json.dumps({'usuarios': event["usuarios"]}))

    @database_sync_to_async
    def get_room(self, room_pk: int, user_pk: int = None) -> Room:
        room = Room.objects.get(id=room_pk)
        if user_pk:
            if not room.current_users.filter(id=user_pk).exists():
                return None

        return room

    @database_sync_to_async
    def create_room_for_user(self, name) -> Room:
        room = Room.objects.create(name=name, room_type="PB")
        room.current_users.add(User.objects.get(id=self.scope["user"].id))
        room.save()

        return RoomSerializer(room).data

    # @database_sync_to_async
    # def get_public_room(self, pk: int) -> Room:
    #     return Room.objects.get(pk=pk)

    @database_sync_to_async
    def current_users(self, room: Room):
        return [UserSerializer(user).data for user in room.current_users.all()]

    @database_sync_to_async
    def remove_user_from_room(self, room_pk, user_pk):
        room: Room = Room.objects.get(id=room_pk)
        if not room.room_type == "PB":
            return None
        if room.current_users.filter(id=self.scope["user"].id).exists() and room.current_users.filter(id=user_pk).exists():
            room.current_users.remove(User.objects.get(id=user_pk))
            room.save()

        return RoomSerializer(room).data

    @database_sync_to_async
    def add_user_to_room(self, room_pk, user_pk, **kwargs):
        room: Room = Room.objects.get(id=room_pk)
        if not room.room_type == "PB":
            return None
        if room.current_users.filter(id=self.scope["user"].id).exists() and not room.current_users.filter(id=user_pk).exists():
            room.current_users.add(User.objects.get(id=user_pk))
            room.save()
        return RoomSerializer(room).data
        # user: User = self.scope["user"]
        # if not user.current_rooms.filter(pk=self.room_subscribe).exists():
        #     user.current_rooms.add(Room.objects.get(pk=pk))

    @database_sync_to_async
    def get_private_room(self, user_pk: int) -> Room:
        try:

            # room = Room.objects.filter(current_users__id=user_pk).filter(
            #     current_users__id=self.scope["user"].id).get()
            # obj['room_is'] = 'exist'
            room = Room.objects.raw('''SELECT "chat_room"."id", "chat_room"."room_type"
                                        FROM "chat_room"
                                        where exists(
                                            select *
                                             from "chat_room_current_users"
                                             where "chat_room"."id" = "chat_room_current_users"."room_id"
                                              and "chat_room_current_users"."user_id" = 4)
                                         and exists(
                                             select *
                                              from "chat_room_current_users"
                                              where "chat_room"."id" = "chat_room_current_users"."room_id"
                                               and "chat_room_current_users"."user_id" = 2)
                                        order by "chat_room"."id"''')[0]
        except IndexError:
            room = Room(room_type="PR")
            room.save()
            room.current_users.add(User.objects.get(id=user_pk))
            room.current_users.add(User.objects.get(id=self.scope["user"].id))
            room.save()
            # obj['room_is'] = 'new'
        return room

    # @database_sync_to_async
    # def apply_unread_message(self, message_obj):
    #     users = Room.objects.get(pk=self.room_subscribe).current_users.exclude(
    #         id=self.scope["user"].id)
    #     for user in users:
    #         try:
    #             unread_message = UnreadMessage.objects.get(
    #                 user=user.id, room=self.room_subscribe)
    #         except UnreadMessage.DoesNotExist:
    #             unread_message = UnreadMessage.objects.create(
    #                 user_id=user.id, room_id=self.room_subscribe)

    #         if not unread_message.last_unread_message:
    #             unread_message.last_unread_message = message_obj
    #             unread_message.save()
    #             return

    #         if unread_message.last_unread_message.id > message_obj.id:
    #             unread_message.last_unread_message = message_obj
    #             unread_message.save()

    @database_sync_to_async
    def move_unread_message(self):
        try:
            unread_message = UnreadMessage.objects.get(
                user=self.room_user_id, room=self.room_subscribe)
            unread_message.last_unread_message = None
            unread_message.save()
        except UnreadMessage.DoesNotExist:
            return
