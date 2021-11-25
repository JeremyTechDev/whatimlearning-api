from django.db.models.aggregates import Count
from django.http.response import HttpResponseRedirect
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from requests_oauthlib import OAuth1
from urllib.parse import urlencode
import requests


from . import models
from .serializers import UserSerializer, ResourceSerializer, TechnologySerializer


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = UserSerializer


class TechnologyViewSet(ModelViewSet):
    serializer_class = TechnologySerializer

    def get_queryset(self):
        return models.Technology.objects.select_related(
            'featured_code'
        ).filter(user=self.kwargs['user_pk'])

    def get_serializer_context(self):
        return {'user_pk': self.kwargs['user_pk']}


class ResourceViewSet(ModelViewSet):
    serializer_class = ResourceSerializer

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
            response.raise_for_status()

            response_split = response.text.split("&")[0]
            oauth_token = response_split.split("=")[1]

            # use token to authenticate with twitter
            return HttpResponseRedirect(f"{settings.TWITTER_AUTH_URL}/authenticate?oauth_token={oauth_token}")
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
            [user, created] = models.User.objects.get_or_create(**user_data)
            user_data.update({ 'id': user.id, 'created': created })

            return Response(user_data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
