from django.conf import settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from requests_oauthlib import OAuth1
from urllib.parse import urlencode
import requests

from .permissions import IsSelf


from . import models
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


class TwitterAuthRedirectEndpoint(APIView):
    def get(self, request):
        try:
            # get auth config to request twitter token
            oauth = OAuth1(
                client_key=settings.TWITTER_API_KEY,
                client_secret=settings.TWITTER_API_SECRET_KEY
            )
            data = urlencode({
                "oauth_callback": settings.TWITTER_AUTH_CALLBACK_URL
            })
            # request twitter token
            response = requests.post(
                f"{settings.TWITTER_AUTH_URL}/request_token",
                auth=oauth,
                data=data,
            )
            print(response.status_code)
            # response.raise_for_status()

            response_split = response.text.split("&")[0]
            oauth_token = response_split.split("=")[1]

            # use token to authenticate with twitter
            return Response({'redirect_to': f"{settings.TWITTER_AUTH_URL}/authenticate?oauth_token={oauth_token}"})
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TwitterCallbackEndpoint(APIView):
    def get(self, request):
        try:
            # if authentication is accepted, get verifier to request user data
            oauth_token = request.query_params.get("oauth_token")
            oauth_verifier = request.query_params.get("oauth_verifier")
            oauth = OAuth1(
                client_key=settings.TWITTER_API_KEY,
                client_secret=settings.TWITTER_API_SECRET_KEY,
                resource_owner_key=oauth_token,
                verifier=oauth_verifier,
            )

            # request user data
            res = requests.post(
                f"{settings.TWITTER_AUTH_URL}/access_token",
                auth=oauth
            )
            res.raise_for_status()

            # parse user data into dictionary
            splitted_res = res.text.split('&')
            auth_data = dict()
            [
                auth_data.update({var.split('=')[0]: var.split('=')[1]})
                for var in splitted_res
            ]

            user_data = {
                'username': auth_data['screen_name'],
                'twitter_id': auth_data['user_id'],
            }

            # get user profile
            profile = requests.get(
                f"{settings.TWITTER_PROFILE_URL}?screen_name={user_data['username']}",
                None,
                {'Authorization': f"Bearer {settings.TWITTER_BEARER}"}
            )

            user_data.update(
                {'profile': profile.json() if profile.status_code == 200 else None}
            )

            [user, created] = models.User.objects.get_or_create(**user_data)
            [token, is_new_token] = Token.objects.get_or_create(user=user)
            user_data.update(
                {
                    'id': user.id,
                    'auth_token': token.key,
                    'created': created
                })

            return Response(user_data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
