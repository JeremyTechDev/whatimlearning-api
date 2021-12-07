from django.conf import settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from requests_oauthlib import OAuth1
from urllib.parse import urlencode
from requests import Response as ResponseInterface
import requests


from . import models


def parse_auth_data(res: ResponseInterface):
    """
    Gets Authentication data from Twitter response text
    """
    auth_data = {}
    splitted_res = res.text.split('&')
    [
        auth_data.update({var.split('=')[0]: var.split('=')[1]})
        for var in splitted_res
    ]

    return {
        'username': auth_data.get('screen_name'),
        'twitter_id': auth_data.get('user_id'),
    }


def get_user_twitter_profile(screen_name: str) -> dict:
    """
    Gets Twitter user profile for name and images info
    """
    profile = requests.get(
        f"{settings.TWITTER_PROFILE_URL}?screen_name={screen_name}",
        headers={'Authorization': f"Bearer {settings.TWITTER_BEARER}"}
    )

    if profile.status_code == 200:
        profile_data = profile.json()
        return {
            'followers': profile_data.get('followers_count', 0),
            'profile_background': profile_data.get('profile_banner_url', None),
            'profile_image': (profile_data.get('profile_image_url_https', '')).removesuffix('_normal'),
            'twitter_name': profile_data.get('name', None),
        }

    return None


def use_get_or_create(user_data: dict) -> dict:
    """
    Gets search fields and defaults for Django `get_or_create` method
    """

    data = dict(user_data)
    username = data.pop('username')
    twitter_id = data.pop('twitter_id')
    return {
        'username': username,
        'twitter_id': twitter_id,
        'defaults': {**data},
    }


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
            return Response({'redirect_to': f"{settings.TWITTER_AUTH_URL}/authenticate?oauth_token={oauth_token}"})
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TwitterCallbackEndpoint(APIView):
    def get(self, request):
        try:
            # if authentication is accepted, get verifier to request user data
            oauth_token = request.query_params.get("oauth_token")
            oauth_verifier = request.query_params.get("oauth_verifier")
            print(oauth_token, oauth_verifier)
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

            # Get user data and profile
            user_data = parse_auth_data(res)
            user_profile = get_user_twitter_profile(user_data.get('username'))
            user_data.update(user_profile)

            print(user_data)
            [user, created] = models.User.objects.get_or_create(
                **use_get_or_create(user_data)
            )
            [token, _] = Token.objects.get_or_create(user=user)
            user_data.update(
                {
                    'id': user.id,
                    'auth_token': token.key,
                    'created': created
                }
            )

            return Response(user_data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
