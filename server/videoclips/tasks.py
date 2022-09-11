from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from django.http import HttpRequest
# from rest_framework.request import Request

# from vidnet.celery import app
from celery import shared_task
from datetime import datetime, timedelta

from users.models import User
from users.serializers import UserProfileSerializer

from .serializers import VideoclipSerializer
from .models import VCCategory, VCSubscription, Videoclip


@shared_task(name='hello2')
def hello2():
    print("HAHA1")


# @app.task(bind=True)
@shared_task(name='get_new_videoclips')
def get_new_videoclips():

    print(f'{datetime.now()} begin sending clips')
    data_users = get_new_videoclips_data()
    for data_user in data_users:

        message_text = render_to_string(
            'mail/new_clips.html', {'clips': data_user['clips'], })

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


def get_new_videoclips_data():
    # print(f'{datetime.now()} begin sending postss1')

    now = timezone.now()
    # seven_days = timedelta(days=-7)

    date_posts = now + timedelta(days=-1)

    clips = Videoclip.objects.filter(create_date__gte=date_posts).values()
    clips = Videoclip.objects.all()

    # for post in posts:
    #     message_text = render_to_string('mail/new_posts.html', { 'clips': user_posts, })

    request = HttpRequest()
    request.method = 'GET'
    # request.META = myOldRequest.META
    # settings.BASE_BACKEND_URL
    request.META['SERVER_NAME'] = 'localhost'
    request.META['SERVER_PORT'] = 8000
    # request.META['']
    serializer_context = {
        'request': request,
    }

    # print(serializer_context)
    clips_serialized = []
    clips_ids = []
    categories_id = []
    for clip_model in clips:
        clips_serialized.append(VideoclipSerializer(
            clip_model, context=serializer_context).data)
        clips_ids.append(clip_model.id)

        # clip_model['post_url'] = f'http://{Site.objects.get_current().domain}:8000/news/{clip_model["id"]}'

    clip_categories = list(
        VCCategory.objects.filter(videoclip__in=clips_ids).values())

    for clip_category in clip_categories:
        categories_id.append(clip_category['category_id'])

    subscribers = VCSubscription.objects.filter(category__in=categories_id).values(
        'id', 'user_id', 'user__email', 'category_id')

    users_ids = set(map(lambda x: x['user_id'], subscribers))
    users = User.objects.filter(id__in=users_ids)
    # for subscriber in subscribers:
    # user_id = subscriber['user_id']
    context_data_array = []
    for user in users:
        user_data = UserProfileSerializer(user).data
        context_data = {'user': user_data}

        user_categories = []
        # email = ''
        for subscriber in subscribers:
            if subscriber['user_id'] == user.id:
                # email = subscriber['user__email']
                user_categories.append(subscriber['category_id'])

        # if email == 'xsami@yandex.ru':
        user_clips_id = []
        for clip_category in clip_categories:
            if clip_category['category_id'] in user_categories:
                user_clips_id.append(clip_category['videoclip_id'])
        user_clips_id = set(user_clips_id)

        user_clips = []
        for user_clip_id in user_clips_id:
            for clip in clips_serialized:
                if clip['id'] == user_clip_id:
                    user_clips.append(clip)

        if user_clips:
            # pass
            # message_text = render_to_string(
            #     'mail/new_clips.html', {'clips': user_clips, })
            # pass
            context_data['clips'] = user_clips
            context_data_array.append(context_data)

    return context_data_array
    #             recipients = [email]

    #             if recipients:
    #                 send_mail('Новые посты',
    #                           message_text,
    #                           settings.EMAIL_HOST_USER,
    #                           recipients,
    #                           html_message=message_text
    #                           )
