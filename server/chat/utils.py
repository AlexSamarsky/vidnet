

from .serializers import UnreadMessageChatSerializer
from .models import UnreadMessage


def get_unread_messages():

    unread_messages = UnreadMessage.objects.filter(last_unread_message_id__isnull=False).filter(
        room__room_type="PR").order_by('user_id').all()

    return UnreadMessageChatSerializer(unread_messages, many=True).data
