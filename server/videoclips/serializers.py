from rest_framework import serializers
from users.serializers import UserSerializer

from videoclips.models import Category, Videoclip


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class VideoclipSerializer(serializers.ModelSerializer):

    categories = CategorySerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Videoclip
        fields = ["title", "description",
                  "categories", "author", "create_date"]
