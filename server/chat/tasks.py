from django.conf import settings
from celery import shared_task

import vonage

from .utils import get_unread_messages


@shared_task(name='test_sms')
def test_sms():
    client = vonage.Client(key=settings.VONAGE_SMS_API_KEY,
                           secret=settings.VONAGE_SMS_SEKRET_KEY)
    sms = vonage.Sms(client)

    unread_messages = get_unread_messages()
    current_user = None
    message_text = 'Unread messages from:\n'
    message_users = ''

    for unread_message in unread_messages:
        if not current_user or current_user['id'] != unread_message['user']['id']:
            if current_user and current_user['phone_number']:
                print('sended sms', message_text, message_users)
                sms.send_message(
                    {
                        "from": "VIDNET",
                        "to": current_user['phone_number'],
                        "text": f"{message_text} {message_users}",
                    }
                )

            current_user = unread_message['user']
            message_users = ''

        message_users += f"- {unread_message['last_unread_message']['user']['name']}\n"
    if current_user and current_user['phone_number']:
        print('sended sms', f"{message_text} {message_users}")

        sms.send_message(
            {
                "from": "VIDNET",
                "to": current_user['phone_number'],
                "text": f"{message_text} {message_users}",
            }
        )

    # if responseData["messages"][0]["status"] == "0":
    #     print("Message sent successfully.")
    #     return

    # print(
    #     f"Message failed with error: {responseData['messages'][0]['error-text']}")
