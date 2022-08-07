from typing import List
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.management.utils import get_random_secret_key


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, db_index=True)
    secret_key = models.CharField(
        max_length=255, default=get_random_secret_key)

    last_login = models.DateTimeField(null=True)
    social = models.CharField(max_length=40, blank=True)

    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: List[str] = []

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    @property
    def name(self):
        if not self.last_name:
            return self.first_name.capitalize()

        return f'{self.first_name.capitalize()} {self.last_name.capitalize()}'