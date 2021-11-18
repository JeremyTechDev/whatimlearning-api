from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from . import models


class ResourceItemInline(admin.StackedInline):
    model = models.Resource
    extra = 0


class FeaturedCodeItemInline(admin.StackedInline):
    model = models.FeaturedCode


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'first_name', 'last_name',
                    'twitter_id', 'is_staff', 'is_superuser']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'twitter_id'),
        }),
    )


@admin.register(models.Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['title', 'description',
                    'resources_count', 'code', 'last_update']
    search_fields = ['title__istartswith']
    list_prefetch_related = ['resources']
    inlines = [FeaturedCodeItemInline, ResourceItemInline]

    @admin.display(ordering='code')
    def code(self, technology):
        url = (reverse('admin:core_featuredcode_changelist')
               + '?'
               + urlencode({'technology__id': str(technology.id)}))
        return format_html('<a href="{}">{}</a>', url, technology.featured_code)

    @admin.display(ordering='resources_count')
    def resources_count(self, technology):
        url = (reverse('admin:core_resource_changelist')
               + '?'
               + urlencode({'technology__id': str(technology.id)}))
        return format_html('<a href="{}">{}</a>', url, technology.resources_count)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('featured_code').annotate(
            resources_count=Count('resources')
        )


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'attached_to', 'url']
    list_filter = ['is_free']
    list_select_related = ['technology']
    search_fields = ['title__istartswith']

    @admin.display(ordering='attached_to')
    def attached_to(self, resource):
        url = (reverse('admin:core_technology_changelist')
               + '?'
               + urlencode({'id': str(resource.technology.id)}))
        return format_html('<a href="{}">{}</a>', url, resource.technology)


@admin.register(models.FeaturedCode)
class FeaturedCodeAdmin(admin.ModelAdmin):
    list_display = ['language', 'code', 'attached_to']
    list_filter = ['language']
    list_select_related = ['technology']
    search_fields = ['language__istartswith']

    @admin.display(ordering='attached_to')
    def attached_to(self, featured_code):
        url = (reverse('admin:core_technology_changelist')
               + '?'
               + urlencode({'id': str(featured_code.technology.id)}))
        return format_html('<a href="{}">{}</a>', url, featured_code.technology)
