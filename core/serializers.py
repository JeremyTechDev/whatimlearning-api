from rest_framework import serializers
from . import models


class FeaturedCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FeaturedCode
        fields = ['code', 'language']


class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Resource
        fields = ['id', 'url', 'is_free']

    def create(self, validated_data):
        technology_id = self.context['technology_pk']
        return models.Resource.objects.create(technology_id=technology_id, **validated_data)


class TechnologySerializer(serializers.ModelSerializer):
    featured_code = FeaturedCodeSerializer(required=False, allow_null=True)
    resources = ResourceSerializer(many=True, read_only=True)

    def create(self, validated_data):
        user_id = self.context['user_pk']

        if validated_data.get('featured_code'):
            featured_code = validated_data.pop('featured_code')
            technology = models.Technology(user=user_id, **validated_data)
            featured_code = models.FeaturedCode(
                technology_id=technology.id,
                **featured_code,
            )
            technology.featured_code = featured_code
            technology.save()
            return technology
        else:
            technology = models.Technology(user=user_id, **validated_data)
            technology.save()
            return technology

    def update(self, instance, validated_data):
        user_id = self.context['user_pk']

        if validated_data.get('featured_code'):
            featured_code = models.FeaturedCode.objects.update_or_create(
                technology_id=instance.id,
                defaults={**validated_data.get('featured_code')}
            )
            validated_data['featured_code'] = featured_code[0]
        else:
            featured_code = models.FeaturedCode.objects.get(
                technology_id=instance.id
            )
            featured_code.delete()
            validated_data['featured_code'] = None

        instance = models.Technology(user=user_id, **validated_data)
        instance.save()
        return instance

    class Meta:
        model = models.Technology
        fields = ['id', 'title', 'description', 'cover_img',
                  'featured_code', 'last_update', 'resources']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'twitter_name', 'username', 'twitter_id',
                  'profile_image', 'profile_background']

    def create(self, validated_data):
        return models.User.objects.get_or_create(**validated_data)
