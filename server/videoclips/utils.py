from functools import partial
from typing import Any, Dict

from factory import Factory
from factory.base import StubObject

from django.utils import timezone

from django.http import HttpRequest

from datetime import timedelta

from users.models import User
from users.serializers import UserProfileSerializer

from .serializers import VideoclipSerializer
from .models import VCCategory, VCSubscription, Videoclip


def generate_dict_factory(factory: Factory):
    def convert_dict_from_stub(stub: StubObject) -> Dict[str, Any]:
        stub_dict = stub.__dict__
        for key, value in stub_dict.items():
            if isinstance(value, StubObject):
                stub_dict[key] = convert_dict_from_stub(value)
        return stub_dict

    def dict_factory(factory, **kwargs):
        stub = factory.stub(**kwargs)
        stub_dict = convert_dict_from_stub(stub)
        return stub_dict

    return partial(dict_factory, factory)


def generate_dict_factory_from_stub(factory: Factory):
    def convert_dict_from_stub(stub: StubObject) -> Dict[str, Any]:
        stub_dict = stub.__dict__
        for key, value in stub_dict.items():
            if isinstance(value, StubObject):
                stub_dict[key] = convert_dict_from_stub(value)
        return stub_dict

    def dict_factory(factory):
        stub = factory
        stub_dict = convert_dict_from_stub(stub)
        return stub_dict

    return partial(dict_factory, factory)


def convert_dict_from_stub(stub: StubObject) -> Dict[str, Any]:
    stub_dict = stub.__dict__
    for key, value in stub_dict.items():
        if isinstance(value, StubObject):
            stub_dict[key] = convert_dict_from_stub(value)
    return stub_dict


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
