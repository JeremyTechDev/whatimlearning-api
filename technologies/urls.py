from django.urls import include, path
from rest_framework_nested import routers

from . import views


router = routers.SimpleRouter()
router.register('technologies', views.TechnologyViewSet)

technologies_router = routers.NestedSimpleRouter(
    router,
    'technologies',
    lookup='technology'  # will include technology_pk in kwargs
)
technologies_router.register(
    'resources',
    views.TechnologyResourceViewSet,
    basename='technology-resources'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(technologies_router.urls)),
]
