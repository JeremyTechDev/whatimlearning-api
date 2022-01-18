from rest_framework import serializers
from rest_framework.authtoken.models import Token
from . import models


class FeaturedCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FeaturedCode
        fields = ['code', 'language']


class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Resource
        fields = ['id', 'url', 'is_free', 'technology']

    def create(self, validated_data):
        return models.Resource.objects.create(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'twitter_name', 'username', 'twitter_id',
                  'profile_image', 'profile_background']

    def create(self, validated_data):
        return models.User.objects.get_or_create(**validated_data)


class TechnologySerializer(serializers.ModelSerializer):
    featured_code = FeaturedCodeSerializer(required=False, allow_null=True)
    resources = ResourceSerializer(many=True, read_only=True)
    user = UserSerializer(required=False, allow_null=True, read_only=True)

    def create(self, validated_data):
        user_id = self.context['user_pk']
        technology = models.Technology(user_id=user_id, **validated_data)
        technology.save()
        return technology

    def update(self, instance, validated_data):
        user_id = self.context['user_pk']
        instance = models.Technology(user_id=user_id, **validated_data)
        instance.save()
        return instance

    class Meta:
        model = models.Technology
        fields = ['id', 'title', 'description', 'cover_img',
                  'featured_code', 'last_update', 'resources', 'user']


class TokenSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Token
        fields = ['user']
