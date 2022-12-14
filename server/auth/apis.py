# from urllib.parse import urlencode

from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView

from rest_framework_simplejwt.views import TokenObtainPairView

from django.urls import reverse

from django.conf import settings
from django.shortcuts import redirect
from django.utils.http import urlencode

from api.mixins import ApiErrorsMixin, PublicApiMixin, ApiAuthMixin

from users.services import user_record_login, user_change_secret_key

from auth.services import google_get_access_token, google_get_user_info

from .compat import set_cookie_with_token
from .serializers import VidnetObtainPairSerializer, UserRegisterSerializer

from users.services import user_create


class LoginApi(ApiErrorsMixin, TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = VidnetObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Reference: https://github.com/Styria-Digital/django-rest-framework-jwt/blob/master/src/rest_framework_jwt/views.py#L44
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get('refresh')

        user = serializer.user  # or request.user
        user_record_login(user=user)

        response = super().post(request, *args, **kwargs)

        set_cookie_with_token(
            response, settings.AUTH_REFRESH_TOKEN_COOKIE_NAME, refresh_token)

        return response


class GoogleLoginApi(PublicApiMixin, ApiErrorsMixin, TokenObtainPairView):
    serializer_class = VidnetObtainPairSerializer

    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get('code')
        error = validated_data.get('error')

        login_url = f'{settings.BASE_FRONTEND_URL}/login'

        if error or not code:
            params = urlencode({'error': error})
            return redirect(f'{login_url}?{params}')

        domain = settings.BASE_BACKEND_URL
        api_uri = reverse('api:v1:auth:login-with-google')
        redirect_uri = f'{domain}{api_uri}'

        access_token = google_get_access_token(
            code=code, redirect_uri=redirect_uri)

        user_data = google_get_user_info(access_token=access_token)

        profile_data = {
            'email': user_data['email'],
            'first_name': user_data.get('given_name', ''),
            'last_name': user_data.get('family_name', ''),
            'password': code,
            'social': 'google'
        }

        # serializer = self.get_serializer(data=request.data)
        serializer = VidnetObtainPairSerializer(data=profile_data)

        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get('refresh')

        user = serializer.user  # or request.user
        user_record_login(user=user)

        refresh = serializer.get_token(user)
        data = {}
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data['username'] = user.first_name
        response = Response(data, status=status.HTTP_200_OK)

        set_cookie_with_token(
            response, settings.AUTH_REFRESH_TOKEN_COOKIE_NAME, data["refresh"])

        # # We use get-or-create logic here for the sake of the example.
        # # We don't have a sign-up flow.
        # user, _ = user_get_or_create(**profile_data)

        url_redirect = f"{settings.BASE_FRONTEND_URL}?{urlencode(data)}"
        response = redirect(url_redirect)
        set_cookie_with_token(
            response, settings.AUTH_REFRESH_TOKEN_COOKIE_NAME, refresh_token)
        # response = jwt_login(response=response, user=user)

        return response


class LogoutApi(ApiAuthMixin, ApiErrorsMixin, APIView):
    def post(self, request):
        """
        Logs out user by removing JWT cookie header.
        """
        user_change_secret_key(user=request.user)

        response = Response(status=status.HTTP_202_ACCEPTED)
        response.delete_cookie(settings.AUTH_REFRESH_TOKEN_COOKIE_NAME)

        return response


class SignInApi(PublicApiMixin, ApiErrorsMixin, CreateAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = UserRegisterSerializer

    # @action(methods=['POST', ], detail=False)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_create(**serializer.validated_data)
        # data = serializers.AuthUserSerializer(user).data
        return Response(status=status.HTTP_201_CREATED)
