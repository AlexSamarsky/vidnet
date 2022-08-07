# from rest_framework import serializers
# from django.contrib.auth import authenticate, get_user_model
# from utils import (
#     unix_epoch,
# )
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# class TokenUserSerializer(serializers.Serializer):

#     password = serializers.CharField(
#         write_only=True, required=True, style={'input_type': 'password'})
#     token = serializers.CharField(read_only=True)

#     def __init__(self, *args, **kwargs):
#         super(TokenUserSerializer, self).__init__(*args, **kwargs)

#         self.fields[self.username_field
#                     ] = serializers.CharField(write_only=True, required=True)

#     @property
#     def username_field(self):
#         return get_user_model().USERNAME_FIELD

#     def validate(self, data):
#         credentials = {
#             self.username_field: data.get(self.username_field),
#             'password': data.get('password')
#         }
#         user = authenticate(self.context['request'], **credentials)

#         if not user:
#             msg = 'Unable to log in with provided credentials.'
#             raise serializers.ValidationError(msg)

#         return {
#             'token': '',
#             'user': user,
#             # 'issued_at': payload.get('iat', unix_epoch())
#         }


class VidnetObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(VidnetObtainPairSerializer, cls).get_token(user)

        token['username'] = user.first_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.first_name

        return data
