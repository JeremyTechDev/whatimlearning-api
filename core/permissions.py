from rest_framework.permissions import BasePermission


class IsSelf(BasePermission):

    def has_permission(self, request, view):
        args = (request.parser_context.get(
            'kwargs', {}))

        # Get corrent pk ('pk' for user requests and 'user_pk' for non-user requests)
        user_pk = args.get('user_pk', None)
        user_pk = args.get('pk', None) if user_pk is None else user_pk

        return bool(str(request.user.id) == user_pk)
