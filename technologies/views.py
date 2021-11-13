from django.db.models.aggregates import Count
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from . import models
from technologies.serializers import ResourceSerializer, TechnologySerializer


class TechnologyViewSet(ModelViewSet):
    queryset = models.Technology.objects.select_related(
        'featured_code'
    ).annotate(resource_count=Count('resource')).all()
    serializer_class = TechnologySerializer


class ResourceViewSet(ModelViewSet):
    serializer_class = ResourceSerializer

    def get_queryset(self):
        return models.Resource.objects.filter(technology_id=self.kwargs['technology_pk'])

    def get_serializer_context(self):
        return {'technology_pk': self.kwargs['technology_pk']}

    def post(self, request):
        is_many = isinstance(request.data, list)
        serializer = ResourceSerializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
