import factory
from .models import Category, Reaction, Videoclip
# from users.factories import UserFactory


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        # database = 'test'

    name = factory.Sequence(lambda n: f"Category {n}")


class ReactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reaction

    name = "Лайк"
    icon = "HRT"


class VideoclipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Videoclip

    title = factory.Faker('name')
    # author = factory.SubFactory(UserFactory)
    description = factory.Faker(
        "sentence",
        nb_words=10,
        variable_nb_words=True
    )
