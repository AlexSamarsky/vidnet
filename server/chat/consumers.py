import json
from django.core.exceptions import PermissionDenied

# from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
# from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer.generics import (
    ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer
from djangochannelsrestframework.scope_utils import request_from_scope, ensure_async

from users.models import User

from .permissions import RoomPermission
from .models import Room, Message, UnreadMessage
from .serializers import MessageSerializer, RoomNotifySerializer, UserSerializer, RoomChatSerializer


class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomChatSerializer
    permission_classes = [RoomPermission]
    lookup_field = "pk"

    async def disconnect(self, code):
        # if hasattr(self, "room_subscribe"):
        #     # await self.remove_user_from_room(self.room_subscribe)
        #     self.room_subscribe = None
        #     await self.notify_users()
        await super().disconnect(code)

    @action()
    async def join_private_room(self, action, user_pk, **kwargs):
        obj = {
            'user_pk': user_pk,
            'scope_user_pk': self.scope["user"].id
        }
        room, room_data = await self.get_private_room(user_pk)
        await self.check_object_permissions(action, room)
        obj['room'] = room_data

        # self.room_subscribe = room.id
        self.room_user_id = self.scope["user"].id
        await self.message_activity.subscribe(room=room.id)
        # await self.notify_users()
        return obj, 200

    @action()
    async def join_public_room(self, action, room_pk, user_pk, **kwargs):
        obj = {
            'scope_user_pk': self.scope["user"].id
        }
        room, room_data = await self.get_room(room_pk, user_pk)
        await self.check_object_permissions(action, room)
        if room:
            obj['room'] = room_data

            # self.room_subscribe = room['pk']
            self.room_user_id = self.scope["user"].id
            await self.message_activity.subscribe(room=room['pk'])
            # await self.notify_users()
            return obj, 200

    @action()
    async def join_notification_room(self, **kwargs):
        obj = {
            'scope_user_pk': self.scope["user"].id
        }
        room, room_data = await self.get_notification_room(self.scope['user'].id)
        if room:
            obj['room'] = room_data

            # self.room_subscribe = room.id
            self.room_user_id = self.scope["user"].id
            await self.message_activity.subscribe(room=room.id)
            # await self.notify_users()
            return obj, 200

    @action()
    async def subscribe_all_rooms(self, **kwargs):
        await self.get_notification_room(self.scope['user'].id)
        self.room_user_id = self.scope["user"].id
        rooms = await self.get_user_rooms()
        obj = {'rooms': rooms}
        for room in rooms:
            await self.message_activity.subscribe(room=room['pk'])

        return obj, 200

    @action()
    async def create_message(self, action, room_pk, message, **kwargs):
        room, _ = await self.get_room(room_pk=room_pk)
        await self.check_object_permissions(action, room)
        await database_sync_to_async(Message.objects.create)(
            room=room,
            user=self.scope["user"],
            text=message
        )
        # await self.apply_unread_message(message_obj)

    @staticmethod
    async def init_consumer(self):
        pass

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
    async def subscribe_to_messages_in_room(self, action, room_pk, **kwargs):
        room, room_data = await self.get_room(room_pk=room_pk, user_pk=self.scope['user'].id)
        await self.check_object_permissions(action, room)
        if not room:
            return {"error": "illegible room"}, 404

        # self.room_subscribe = room_pk
        self.room_user_id = self.scope["user"].id
        await self.message_activity.subscribe(room=room_pk)

        obj = {'room': room_data}

        return obj, 200

    @model_observer(Message)
    async def message_activity(self, message, observer=None, **kwargs):
        if not message['data']['user']['id'] == self.scope['user'].id:
            await self.move_unread_message(message['data']['room']['id'], message['data']['user']['id'])

        try:
            action = 'check'
            room, _ = await self.get_room(message['data']['room']['id'])
            await self.check_object_permissions(action, room)
            await self.send_json(message)
        except PermissionDenied:
            pass

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

    # async def notify_users(self):
    #     room, _ = await self.get_room(pk_room=self.room_subscribe)
    #     if self.groups:
    #         for group in self.groups:
    #             await self.channel_layer.group_send(
    #                 group,
    #                 {
    #                     'type': 'update_users',
    #                     'usuarios': await self.current_users(room)
    #                 }
    #             )

    async def update_users(self, event: dict):
        await self.send(text_data=json.dumps({'usuarios': event["usuarios"]}))

    @database_sync_to_async
    def create_room_for_user(self, name) -> Room:
        room = Room.objects.create(name=name, room_type="PB")
        room.current_users.add(User.objects.get(id=self.scope["user"].id))
        room.save()

        return self.get_serializer_class()(room).data

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
            added_user = User.objects.get(id=user_pk)
            room.current_users.remove(added_user)
            room.save()

            obj_nt = {
                'action': 'remove_from_public_room', 'room': RoomNotifySerializer(room).data}
            self.notificate(added_user, json.dumps(obj_nt))

        return self.get_serializer_class()(room).data

    @database_sync_to_async
    def add_user_to_room(self, room_pk, user_pk, **kwargs):
        room: Room = Room.objects.get(id=room_pk)
        if not room.room_type == "PB":
            return None
        if room.current_users.filter(id=self.scope["user"].id).exists() and not room.current_users.filter(id=user_pk).exists():
            added_user = User.objects.get(id=user_pk)
            room.current_users.add(added_user)
            room.save()

            # room_nt = Room.objects.get_or_create(user_pk=user_pk, room_type='NT')
            # room_nt, _ = self.get_user_notification_room(user_pk)
            obj_nt = {
                'action': 'add_to_public_room', 'room': RoomNotifySerializer(room).data}
            self.notificate(added_user, json.dumps(obj_nt))
            # Message.objects.create(
            # room=room_nt, user=added_user, text=json.dumps(obj_nt))
            # Message.objects.create(room=room_nt, user)

        return self.get_serializer_class()(room).data
        # user: User = self.scope["user"]
        # if not user.current_rooms.filter(pk=self.room_subscribe).exists():
        #     user.current_rooms.add(Room.objects.get(pk=pk))

    @database_sync_to_async
    def get_room(self, room_pk: int, user_pk: int = None) -> Room:
        room = Room.objects.get(id=room_pk)
        # if user_pk:
        #     if not room.current_users.filter(id=user_pk).exists():
        #         return None, None

        return room, self.get_serializer_class()(room).data

    @database_sync_to_async
    def get_notification_room(self, user_pk) -> Room:
        room, room_data = self.get_user_notification_room(user_pk)
        return room, room_data

    @database_sync_to_async
    def get_private_room(self, user_pk: int) -> Room:
        try:
            room_type = 'PR'

            room = Room.objects.raw(f'''SELECT "chat_room"."id", "chat_room"."room_type"
                                        FROM "chat_room"
                                        where "chat_room"."room_type" = '{room_type}'
                                         and exists(
                                            select *
                                             from "chat_room_current_users"
                                             where "chat_room"."id" = "chat_room_current_users"."room_id"
                                              and "chat_room_current_users"."user_id" = {user_pk})
                                         and exists(
                                             select *
                                              from "chat_room_current_users"
                                              where "chat_room"."id" = "chat_room_current_users"."room_id"
                                               and "chat_room_current_users"."user_id" = {self.scope['user'].id})
                                        order by "chat_room"."id"''')[0]
        except IndexError:
            room = Room(room_type=room_type)
            room.save()
            room.current_users.add(User.objects.get(id=user_pk))
            room.current_users.add(User.objects.get(id=self.scope["user"].id))
            room.save()
            # obj['room_is'] = 'new'
        return room, self.get_serializer_class()(room).data

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
    def move_unread_message(self, room_pk, user_pk):
        try:
            unread_message = UnreadMessage.objects.get(
                user=user_pk, room=room_pk)
            unread_message.last_unread_message = None
            unread_message.save()
        except UnreadMessage.DoesNotExist:
            return

    @database_sync_to_async
    def get_user_rooms(self):
        # RoomChatSerializer(user.current_rooms.all(), many=True).data
        return RoomChatSerializer(self.scope['user'].current_rooms.all(), many=True).data

    # @action
    # async def get_permissions(self, action):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     return [permission() for permission in self.permission_classes]

    async def check_object_permissions(self, action, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        request = request_from_scope(self.scope)

        for permission in await self.get_permissions(action):
            if not await ensure_async(permission.permission.has_object_permission)(request, self, obj):
                self.permission_denied(
                    request,
                    message=getattr(permission, 'message', None),
                    code=getattr(permission, 'code', None)
                )

    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        raise PermissionDenied()

    def notificate(self, user, text):
        room_nt, _ = self.get_user_notification_room(user.id)
        # obj_nt = {
        #     'action': 'new_public_room', 'room': RoomNotifySerializer(room).data}
        Message.objects.create(
            room=room_nt, user=user, text=text)

    def get_user_notification_room(self, user_pk):
        room_type = 'NT'
        try:
            rooms = Room.objects.raw(f'''SELECT "chat_room"."id", "chat_room"."room_type"
                                            FROM "chat_room"
                                            where "chat_room"."room_type" = '{room_type}'
                                                and exists(
                                                select *
                                                from "chat_room_current_users"
                                                where "chat_room"."id" = "chat_room_current_users"."room_id"
                                                and "chat_room_current_users"."user_id" = {user_pk})
                                            order by "chat_room"."id"''')
            room = rooms[0]
        except IndexError:
            room = Room(room_type=room_type)
            room.save()
            room.current_users.add(User.objects.get(id=self.scope["user"].id))
            room.save()
        return room, self.get_serializer_class()(room).data
