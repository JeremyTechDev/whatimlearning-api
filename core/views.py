from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from . import models
from .permissions import IsSelf
from .serializers import UserSerializer, ResourceSerializer, TechnologySerializer


class UserByUsernameViewSet(RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_queryset(self):
        return models.User.objects.filter(username=self.kwargs['username'])


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsSelf()]

    def get_queryset(self):
        """
        Optionally restricts the returned user by
        filtering against a `q` query parameter in the URL.
        """
        queryset = models.User.objects.order_by('followers', 'username').all()
        query = self.request.query_params.get('q')
        if query is not None:
            queryset = queryset.filter(username__icontains=query)

        return queryset


class TechnologyListViewSet(ListAPIView):
    serializer_class = TechnologySerializer

    def get_queryset(self):

        queryset = models.Technology.objects.select_related(
            'featured_code', 'user').prefetch_related('resources').all()
        select_random = self.request.query_params.get('random')
        if select_random is not None:
            queryset = queryset.order_by('?')[0:3]

        return queryset


class TechnologyViewSet(ModelViewSet):
    serializer_class = TechnologySerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsSelf()]

    def get_queryset(self):
        return models.Technology.objects.select_related(
            'featured_code', 'user'
        ).prefetch_related('resources').filter(user=self.kwargs['user_pk'])

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


class GetUserFromToken(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        return Response(UserSerializer(request.user).data)
