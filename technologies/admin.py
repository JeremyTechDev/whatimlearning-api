from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


class ResourceItemInline(admin.StackedInline):
    model = models.Resource
    extra = 0


@admin.register(models.Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'resources_count', 'last_update']
    search_fields = ['title__istartswith']
    list_prefetch_related = ['resources']
    inlines = [ResourceItemInline]

    @admin.display(ordering='resources_count')
    def resources_count(self, technology):
        url = (reverse('admin:technologies_resource_changelist')
               + '?'
               + urlencode({'technology__id': str(technology.id)}))
        return format_html('<a href="{}">{}</a>', url, technology.resources_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            resources_count=Count('resource')
        )


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'technology', 'url']
    list_filter = ['is_free']
    list_select_related = ['technology']
    search_fields = ['title__istartswith']


@admin.register(models.FeaturedCode)
class FeaturedCodeAdmin(admin.ModelAdmin):
    list_display = ['language', 'code', 'technology']
    list_filter = ['language']
    list_select_related = ['technology']
    search_fields = ['language__istartswith']
