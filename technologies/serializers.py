from rest_framework import serializers
from . import models


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Technology
        fields = ['id', 'title', 'description', 'cover_img', 'last_update']


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Resource
        fields = ['id', 'title', 'description', 'url', 'is_free', 'technology']
