from rest_framework import serializers
from . import models
import technologies


class FeaturedCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FeaturedCode
        fields = ['code', 'language']


class TechnologySerializer(serializers.ModelSerializer):
    featured_code = FeaturedCodeSerializer(required=False, allow_null=True)
    resource_count = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        if validated_data.get('featured_code'):
            featured_code = validated_data.pop('featured_code')
            technology = models.Technology(**validated_data)
            featured_code = models.FeaturedCode(
                technology_id=technology.id,
                **featured_code,
            )
            technology.featured_code = featured_code
            technology.save()
            return technology
        else:
            technology = models.Technology(**validated_data)
            technology.save()
            return technology

    def update(self, instance, validated_data):
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

        instance = models.Technology(**validated_data)
        instance.save()
        return instance

    class Meta:
        model = models.Technology
        fields = ['id', 'title', 'description', 'cover_img',
                  'featured_code', 'last_update', 'resource_count']


class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Resource
        fields = ['id', 'title', 'description', 'url', 'is_free']

    def create(self, validated_data):
        technology_id = self.context['technology_pk']
        return models.Resource.objects.create(technology_id=technology_id, **validated_data)
