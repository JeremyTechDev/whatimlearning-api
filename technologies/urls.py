from django.urls import path

from . import views

urlpatterns = [
    path('health/', views.health_check),
    path('technologies/', views.technologies_list),
    path('technologies/<int:id>/', views.technology_details),
    path('technologies/<int:id>/resources', views.technology_resources),
    path('resources/', views.resources_list),
    path('resources/<int:id>/', views.resource_details),
]
