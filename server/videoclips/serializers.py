from django.db import transaction
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Category, VCCategory, VCComment, Videoclip


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class VideoclipSerializer(serializers.ModelSerializer):

    categories = CategorySerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:videoclips:videoclip-detail')

    class Meta:
        model = Videoclip
        fields = ["id", "title", "description",
                  "categories", "author", "create_date", "url"]
        read_only_fields = ['url']


class VideoclipEditSerializer(serializers.ModelSerializer):

    # categories = CategorySerializer(read_only=True, many=True)
    categories = serializers.ListField(
        required=False, child=serializers.IntegerField())
    # categories = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=Category.objects.all(), required=False)

    class Meta:
        model = Videoclip
        fields = '__all__'
        read_only_fields = ('author', )

    @transaction.atomic
    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        ModelClass = self.Meta.model
        new_object = ModelClass.objects.create(**validated_data)
        if categories:
            for category in categories:
                new_object.categories.add(Category.objects.get(id=category))
        new_object.save()
        # raise serializers.ValidationError("ошибка запроса")
        return new_object

    def update(self, instance: Videoclip, validated_data):
        categories = validated_data.pop('categories', None)
        if not categories is None:
            instance.categories.clear()
            for category in categories:
                instance.categories.add(Category.objects.get(id=category))

        return super().update(instance, validated_data)


class VCCommentSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = VCComment
        fields = ['id', 'user', 'create_date', 'comment']


class VCCommentEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = VCComment
        fields = ['id', 'create_date', 'comment']


class VCCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = VCCategory
        fields = ['videoclip', 'category']
