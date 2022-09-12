from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

from celery import shared_task

from .utils import get_new_videoclips_data


@shared_task(name='hello')
def hello():
    print("test")


# @app.task(bind=True)
@shared_task(name='get_new_videoclips')
def get_new_videoclips():

    print(f'{datetime.now()} begin sending clips')
    data_users = get_new_videoclips_data()
    for data_user in data_users:

        message_text = render_to_string(
            'mail/new_clips.html', {'clips': data_user['clips'], })
        print(message_text)
        recipients = [data_user['user']['email']]
        # print(message_text)
        if recipients and message_text:
            send_mail('Новые посты',
                      message_text,
                      settings.EMAIL_HOST_USER,
                      recipients,
                      html_message=message_text
                      )

    # print(f'{datetime.now()} complete sending posts')
