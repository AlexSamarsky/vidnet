from django.urls import reverse

# import json


from rest_framework.test import APITestCase
from rest_framework import status
from auth.serializers import VidnetObtainPairSerializer

from users.models import User

# TokenObtainSerializer.get_token(user)


class AuthorizedMethodTestCase(APITestCase):

    user_data = {'email': 'common@yandex.ru', 'password': '123',
                 'first_name': 'xxx', 'last_name': 'xxx'}

    def setUp(self) -> None:
        self.user = User.objects.create(email=self.user_data['email'], password='123',
                                        first_name='xxx', last_name='xxx')
        self.token = VidnetObtainPairSerializer.get_token(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + str(self.token.access_token))

    def test_me(self):
        response = self.client.get(reverse('api:v1:users:me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user_data['email'])
        self.assertNotEqual(response.data["email"], '123')
        # print(response.data)

    def test_me_not_authorised(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer 123")
        response = self.client.get(reverse('api:v1:users:me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
