# from faker import factory
from rest_framework.test import APITestCase
from django.urls import reverse

from users.factories import UserFactory, SuperUserFactory
# from .serializers import VideoclipEditSerializer
from .factories import CategoryFactory, VideoclipFactory

from auth.serializers import VidnetObtainPairSerializer

# from django.core import serializers
from .utils import convert_dict_from_stub
from json import dumps


class AuthorizedMethodTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = UserFactory.create()
        self.author = UserFactory.create()
        self.admin = SuperUserFactory.create()

        self.user_token = VidnetObtainPairSerializer.get_token(user=self.user)
        self.user_access_token = str(self.user_token.access_token)
        # print(self.user_access_token)

        self.author_token = VidnetObtainPairSerializer.get_token(
            user=self.author)
        self.author_access_token = str(self.author_token.access_token)

        self.admin_token = VidnetObtainPairSerializer.get_token(
            user=self.admin)
        self.admin_access_token = str(self.admin_token.access_token)

        self.categories = CategoryFactory.create_batch(size=2)

        self.url_videoclip_create = reverse('api:v1:videoclips:videoclip-list')

        return super().setUp()

    def test_create_without_auth(self):

        # print(self.author)
        vc = VideoclipFactory.stub(author=self.author.id)
        # factory.build
        # t = VideoclipEditSerializer(data=vc)
        # js2 = generate_dict_factory(VideoclipFactory)
        # js3 = generate_dict_factory_from_stub(vc)
        # print(js2)
        # print(js3)
        js4 = convert_dict_from_stub(vc)
        print(dumps(js4))
        # js = serializers.serialize("json", vc, fields=('title', 'description'))
        response = self.client.post(self.url_videoclip_create, dumps(js4))
        print(response)
        # print(js)
        # print(vc.author)
