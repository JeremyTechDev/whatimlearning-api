from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from . import models
from .permissions import IsSelf
from .serializers import UserSerializer, ResourceSerializer, TechnologySerializer


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = UserSerializer


class TechnologyListViewSet(ListAPIView):
    queryset = models.Technology.objects.select_related('featured_code').all()
    serializer_class = TechnologySerializer


class TechnologyViewSet(ModelViewSet):
    serializer_class = TechnologySerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsSelf()]

    def get_queryset(self):
        return models.Technology.objects.select_related(
            'featured_code'
        ).filter(user=self.kwargs['user_pk'])

    def get_serializer_context(self):
        return {'user_pk': self.kwargs['user_pk']}


class ResourceViewSet(ModelViewSet):
    serializer_class = ResourceSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsSelf()]

    def get_queryset(self):
        return models.Resource.objects.filter(technology=self.kwargs['technology_pk'])

    def get_serializer_context(self):
        return {'technology_pk': self.kwargs['technology_pk']}

    def post(self, request):
        is_many = isinstance(request.data, list)
        serializer = ResourceSerializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
