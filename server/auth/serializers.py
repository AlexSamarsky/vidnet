# from rest_framework import serializers
# from django.contrib.auth import authenticate, get_user_model
# from utils import (
#     unix_epoch,
# )
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import BaseUserManager


User = get_user_model()


class VidnetObtainPairSerializer(TokenObtainPairSerializer):

    social = serializers.CharField(required=False, default='')
    first_name = serializers.CharField(
        required=False, default='', allow_blank=True)
    last_name = serializers.CharField(
        required=False, default='', allow_blank=True)
    context = {}

    @classmethod
    def get_token(cls, user):
        token = super(VidnetObtainPairSerializer, cls).get_token(user)

        token['username'] = user.first_name
        return token

    def validate(self, attrs):
        self.context = {'request': {'social': attrs['social'],
                                    'first_name': attrs['first_name'],
                                    'last_name': attrs['last_name'],
                                    }}
        data = super().validate(attrs)
        data['username'] = self.user.first_name

        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A user serializer for registering the user
    """

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name')

    def validate_email(self, value):
        user = User.objects.filter(email=value)
        if user:
            raise serializers.ValidationError("Email is already taken")
        return BaseUserManager.normalize_email(value)

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value
