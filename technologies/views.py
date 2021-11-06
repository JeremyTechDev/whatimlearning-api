from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import models
from technologies.serializers import ResourceSerializer, TechnologySerializer


@api_view()
def health_check(request):
    return Response({'status': 'OK'})


@api_view(['GET', 'POST'])
def technologies_list(request):
    if request.method == 'GET':
        technologies = models.Technology.objects.select_related(
            'featured_code'
        ).annotate(resource_count=Count('resource')).all()
        serializer = TechnologySerializer(technologies, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TechnologySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def technology_details(request, id):
    technology = get_object_or_404(models.Technology.objects.annotate(
        resource_count=Count('resource')).all(), pk=id)

    if request.method == 'GET':
        serializer = TechnologySerializer(technology)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TechnologySerializer(technology, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        technology.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view()
def technology_resources(request, id):
    resources = models.Resource.objects.filter(technology__id=id)
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def resources_list(request):

    if request.method == 'GET':
        resources = models.Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        is_many = isinstance(request.data, list)
        serializer = ResourceSerializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def resource_details(request, id):
    resource = get_object_or_404(models.Resource, pk=id)

    if request.method == 'GET':
        serializer = ResourceSerializer(resource)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ResourceSerializer(resource, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
