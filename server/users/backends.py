from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.services import user_get_or_create

UserModel = get_user_model()


class VidnetBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # user = super().authenticate(request, username=username, password=password, **kwargs)
        # if user:
        #     if user.social == '':
        #         return user
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.social:
                pass

            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class VidnetGoogleBackend(ModelBackend):

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField(
            required=False, default='', allow_blank=True)
        last_name = serializers.CharField(
            required=False, default='', allow_blank=True)
        social = serializers.CharField(
            required=False, default='', allow_blank=True)

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None:
            return
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            data = {**request, 'email': username}
            # data['password'] = get_sec
            serializer = self.InputSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            if serializer.validated_data.get('social') == 'google':
                user, _ = user_get_or_create(**serializer.validated_data)
                return user
        else:
            if user.social == 'google':
                return user
            #     pass
            # if user.check_password(password) and self.user_can_authenticate(user):
