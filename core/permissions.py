from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):

    def has_permission(self, request, view):
        user_pk = (request.parser_context.get(
            'kwargs', {}).get('user_pk', None))
        return bool(str(request.user.id) == user_pk)
