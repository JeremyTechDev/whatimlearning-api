from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


@admin.register(models.FeaturedCode)
class FeaturedCodeAdmin(admin.ModelAdmin):
    list_display = ['language', 'code']
    search_fields = ['language__istartswith']


@admin.register(models.Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'resources_count', 'last_update']
    search_fields = ['title__istartswith']

    @admin.display(ordering='resources_count')
    def resources_count(self, resource):
        url = (reverse('admin:technologies_resource_changelist')
               + '?'
               + urlencode({'technology__id': str(resource.id)}))
        return format_html('<a href="{}">{}</a>', url, resource.resources_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            resources_count=Count('resource')
        )


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title__istartswith']
