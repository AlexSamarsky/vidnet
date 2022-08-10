from django.urls import reverse

# import json

# from users.models import User

# from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework.test import APITestCase
from rest_framework import status

# TokenObtainSerializer.get_token(user)


class RegistrationTestCase(APITestCase):

    def test_registration_common_pass(self):
        data = {'email': 'common@yandex.ru', 'password': '123',
                'first_name': 'xxx', 'last_name': 'xxx'}
        response = self.client.post(
            reverse('api:v1:auth:register'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'password is too common', "".join(response.data['password']))

    def test_registration(self):
        data = {'email': 'xxx@yandex.ru', 'password': '123qweQWE123',
                'first_name': 'xxx', 'last_name': 'xxx'}
        response = self.client.post(
            reverse('api:v1:auth:register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthTestCase(APITestCase):

    def setUp(self) -> None:
        data = {'email': 'xxx@yandex.ru', 'password': '123qweQWE123',
                'first_name': 'xxx', 'last_name': 'xxx'}
        self.client.post(
            reverse('api:v1:auth:register'), data)
        # return super().setUp()

    def test_auth_login_unauthorized(self):

        data = {'email': 'xxx@yandex.ru', 'password': '123qweQWE1231'}
        response = self.client.post(reverse('api:v1:auth:login'), data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_login(self):

        data = {'email': 'xxx@yandex.ru', 'password': '123qweQWE123'}
        response = self.client.post(reverse('api:v1:auth:login'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
