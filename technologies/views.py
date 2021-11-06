from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
        ).all()
        serializer = TechnologySerializer(technologies, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TechnologySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)


@api_view()
def technology_details(request, id):
    technology = get_object_or_404(models.Technology, pk=id)
    serializer = TechnologySerializer(technology)
    return Response(serializer.data)


@api_view()
def technology_resources(request, id):
    resources = models.Resource.objects.filter(technology__id=id)
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)


@api_view()
def resources_list(request):
    resources = models.Resource.objects.all()
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)


@api_view()
def resource_details(request, id):
    technology = get_object_or_404(models.Resource, pk=id)
    serializer = ResourceSerializer(technology)
    return Response(serializer.data)
