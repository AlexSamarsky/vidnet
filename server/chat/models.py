from django.db import models

from users.models import User

# Create your models here.


class Room(models.Model):

    ROOM_TYPES = [
        ('PR', 'private'),
        ('SG', 'single'),
        ('PB', 'public')
    ]

    current_users = models.ManyToManyField(
        User, related_name="current_rooms", blank=True)

    room_type = models.CharField(max_length=10,
                                 verbose_name="Тип комнаты", choices=ROOM_TYPES)

    name = models.CharField(
        max_length=50, verbose_name='Название чата', null=True)

    def __str__(self) -> str:
        return f"{str(self.id)} {self.room_type}"


class Message(models.Model):

    text = models.CharField(verbose_name='Сообщение', max_length=250, )
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Message ({self.user} {self.room})"

    def save(self, *args, **kwargs) -> None:
        message_obj = super().save(*args, **kwargs)

        users = Room.objects.get(pk=self.room_id).current_users.exclude(
            id=self.user_id)
        for user in users:
            try:
                unread_message = UnreadMessage.objects.get(
                    user=user.id, room=self.room_id)
            except UnreadMessage.DoesNotExist:
                unread_message = UnreadMessage.objects.create(
                    user_id=user.id, room_id=self.room_id)

            if not unread_message.last_unread_message:
                unread_message.last_unread_message = self
                unread_message.save()
                return

            if unread_message.last_unread_message_id > self.id:
                unread_message.last_unread_message = self
                unread_message.save()

        return message_obj


class UnreadMessage(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    last_unread_message = models.ForeignKey(
        Message, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return f"Message ({self.user} {self.room} {self.last_unread_message})"
