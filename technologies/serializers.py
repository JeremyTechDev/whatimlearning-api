from rest_framework import serializers
from . import models


class FeaturedCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FeaturedCode
        fields = ['code', 'language']


class TechnologySerializer(serializers.ModelSerializer):
    featured_code = FeaturedCodeSerializer(required=False)
    resource_count = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        if validated_data.get('featured_code', None):
            featured_code = models.FeaturedCode(
                **validated_data.get('featured_code'))
            featured_code.save()
            validated_data['featured_code'] = featured_code
            technology = models.Technology(**validated_data)
            technology.save()
            return technology
        else:
            technology = models.Technology(**validated_data)
            technology.save()
            return technology

    def update(self, instance, validated_data):
        if validated_data.get('featured_code', None):
            featured_code = models.FeaturedCode(
                **validated_data.get('featured_code'))
            featured_code.save()
            validated_data['featured_code'] = featured_code
            technology = models.Technology(**validated_data)
            technology.save()
            return technology
        else:
            instance = models.Technology(**validated_data)
            instance.save()
            return instance

    class Meta:
        model = models.Technology
        fields = ['id', 'title', 'description',
                  'cover_img', 'last_update', 'resource_count']


class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Resource
        fields = ['id', 'title', 'description', 'url', 'is_free']

    def create(self, validated_data):
        technology_id = self.context['technology_pk']
        return models.Resource.objects.create(technology_id=technology_id, **validated_data)
