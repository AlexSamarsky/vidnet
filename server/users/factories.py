# from faker import Faker
# from factory.django import DjangoModelFactory
import factory

from .models import User

# fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        # database = 'test'

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(
        lambda o: f'{o.first_name}@example.com'.lower())
    is_superuser = False
    is_staff = False


class SuperUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        # database = 'test'

    first_name = 'admin'
    last_name = 'admin'
    email = factory.LazyAttribute(
        lambda o: f'{o.first_name}@example.com'.lower())
    is_superuser = True
    is_staff = True
