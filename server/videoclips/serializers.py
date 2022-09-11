from django.db import transaction
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Category, Reaction, UserReaction, VCBan, VCCategory, VCComment, VCReaction, VCSubscription, Videoclip


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class UserReactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserReaction
        fields = '__all__'


class UserReactionEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserReaction
        fields = ['reaction']

    def create(self, validated_data):
        object = super().create(validated_data)
        object.register_reaction()
        return object


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'


class VCReactionSerializer(serializers.ModelSerializer):
    reaction = ReactionSerializer(read_only=True)

    class Meta:
        model = VCReaction
        # fields = '__all__'
        exclude = ('videoclip',)


class UploadSerializer(serializers.ModelSerializer):

    upload = serializers.FileField()

    class Meta:
        model = Videoclip
        fields = ['upload']


class VideoclipSerializer(serializers.ModelSerializer):

    categories = CategorySerializer(read_only=True, many=True)
    reactions = VCReactionSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()

    file_url = serializers.SerializerMethodField()

    author = UserSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='api:v1:videoclips:videoclip-detail', read_only=True)

    class Meta:
        model = Videoclip
        fields = ["id", "author", "title", "description", "create_date",
                  "categories", "reactions", "comments_count", "url", "file_url"]

    def get_comments_count(self, obj):
        return VCComment.objects.filter(videoclip=obj).count()

    def get_file_url(self, obj):
        if obj.upload:
            return self.context['request'].build_absolute_uri(obj.upload.url)

        return ''


class VideoclipEditSerializer(serializers.ModelSerializer):

    # categories = CategorySerializer(read_only=True, many=True)
    categories = serializers.ListField(
        required=False, child=serializers.IntegerField())

    reactions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=VCReaction.objects.all(), required=False)
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
        return new_object

    @transaction.atomic
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
        fields = ['comment']


class VCCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = VCCategory
        fields = ['videoclip', 'category']


class VCBanSerializer(serializers.ModelSerializer):

    banned_user = UserSerializer(read_only=True)

    class Meta:
        model = VCBan
        fields = ['id', 'banned_user', 'term_date']


class VCBanEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = VCBan
        fields = ['banned_user', 'term_date']

    def create(self, validated_data):
        return super().create(validated_data)


class VCSubscriptionEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = VCSubscription
        fields = ['category']


class VCSubscriptionSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = VCSubscription
        fields = ['id', 'user', 'category']
