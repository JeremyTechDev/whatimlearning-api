from django.urls import include, path
from rest_framework_nested import routers

from . import views


router = routers.SimpleRouter()
router.register('users', views.UserViewSet)

user_router = routers.NestedSimpleRouter(
    router,
    'users',
    lookup='user',  # will be included in kwargs as user_pk
)
user_router.register(
    'technologies',
    views.TechnologyViewSet,
    basename='user-technologies'
)

technologies_router = routers.NestedSimpleRouter(
    user_router,
    'technologies',
    lookup='technology'  # will include technology_pk in kwargs
)
technologies_router.register(
    'resources',
    views.ResourceViewSet,
    basename='technology-resources'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(user_router.urls)),
    path('', include(technologies_router.urls)),
    path('technologies/', views.TechnologyListViewSet.as_view()),
    path(
        "auth/twitter/",
        views.TwitterAuthRedirectEndpoint.as_view(),
        name="twitter-login",
    ),
    path(
        "auth/twitter/callback/",
        views.TwitterCallbackEndpoint.as_view(),
        name="twitter-login-callback",
    ),
]
