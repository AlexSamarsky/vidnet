# from faker import factory
from rest_framework.test import APITestCase
from django.urls import reverse

from users.factories import UserFactory, SuperUserFactory
# from .serializers import VideoclipEditSerializer
from .factories import CategoryFactory, VideoclipFactory

from auth.serializers import VidnetObtainPairSerializer
from rest_framework import status
# from django.core import serializers
from .utils import convert_dict_from_stub


class AuthorizedMethodTestCase(APITestCase):

    def setUp(self) -> None:
        self.admin = SuperUserFactory.create()
        self.author = UserFactory.create()
        self.user = UserFactory.create()

        self.user_token = VidnetObtainPairSerializer.get_token(user=self.user)
        self.user_access_token = str(self.user_token.access_token)

        self.author_token = VidnetObtainPairSerializer.get_token(
            user=self.author)
        self.author_access_token = str(self.author_token.access_token)

        self.admin_token = VidnetObtainPairSerializer.get_token(
            user=self.admin)
        self.admin_access_token = str(self.admin_token.access_token)

        self.categories = CategoryFactory.create_batch(size=2)

        self.url_videoclip_list = 'api:v1:videoclips:videoclip-list'
        self.url_videoclip_detail = 'api:v1:videoclips:videoclip-detail'

        self.vc_with_cat = VideoclipFactory.stub(
            categories=[self.categories[0].id])
        self.obj_vc_with_cat = convert_dict_from_stub(self.vc_with_cat)
        self.vc = VideoclipFactory.stub()
        self.obj = convert_dict_from_stub(self.vc)

        return super().setUp()

    def test_videoclip_create_without_auth(self):

        response = self.client.post(reverse(self.url_videoclip_list), self.obj)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_videoclip_create_auth(self):

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.author_access_token)
        response = self.client.post(reverse(self.url_videoclip_list), self.obj)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.vc.title)
        self.assertEqual(response.data['description'], self.vc.description)

        url_videoclip_detail = reverse(
            self.url_videoclip_detail, args=(response.data['id'],))

        response_update = self.client.put(
            url_videoclip_detail, self.obj_vc_with_cat)
        self.assertEqual(response_update.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response_update.data['title'], self.obj_vc_with_cat['title'])
        self.assertEqual(
            response_update.data['categories'][0]['id'], self.categories[0].id)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.user_access_token)

        response_illegal_update = self.client.put(
            url_videoclip_detail, self.obj)
        self.assertEqual(response_illegal_update.status_code,
                         status.HTTP_403_FORBIDDEN)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)

        response_admin_update = self.client.put(
            url_videoclip_detail, self.obj)
        self.assertEqual(response_admin_update.status_code,
                         status.HTTP_201_CREATED)

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.author_access_token)
        response_delete = self.client.delete(
            url_videoclip_detail)

        self.assertEqual(response_delete.status_code,
                         status.HTTP_204_NO_CONTENT)
