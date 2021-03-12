from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Value, ExpressionWrapper, CharField, OuterRef, Subquery
from django.db.models.functions import Concat
from django.forms import widgets


admin.site.unregister(User)
admin.site.unregister(Group)
# https://stackoverflow.com/questions/6589485/django-admin-change-permissions-list

permission_id_str = ExpressionWrapper(
    Concat('content_type__app_label', Value('.'), 'codename'),
    output_field=CharField(),
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    def _has_permissions(self, user1: User, user2: User) -> bool:
        if user1 is None: return False
        if user1.is_superuser: return True

        if user2 is None: return True
        if user2.is_superuser: return False

        user1_permissions = user1.get_user_permissions()
        user2_permissions = user2.get_user_permissions()

        # user1 has at least the same permissions than user2
        return all(
            p in user1_permissions
            for p in user2_permissions
        )

    def has_view_permission(self, request, obj=None):
        return self._has_permissions(request.user, obj) and \
            super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return self._has_permissions(request.user, obj) and \
            super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._has_permissions(request.user, obj) and \
            super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser and 'is_superuser' in form.base_fields:
            form.base_fields['is_superuser'].disabled = True

        if not request.user.is_superuser and not request.user.is_staff \
        and 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].disabled = True

        if not request.user.is_superuser and 'user_permissions' in form.base_fields:
            permissions = form.base_fields['user_permissions']
            user_permissions = request.user.get_user_permissions()
            permissions.queryset = permissions.queryset.annotate(
                permission_id_str=permission_id_str
            ).filter(permission_id_str__in=user_permissions)

        if not request.user.is_superuser and 'groups' in form.base_fields:
            permissions = form.base_fields['groups']
            user_groups = request.user.groups.all()
            permissions.queryset = permissions.queryset.filter(
                id__in=Subquery(user_groups.values('id'))
            )

        return form


@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    def _has_permissions(self, user: User, group: Group) -> bool:
        if user is None: return False
        if user.is_superuser: return True
        if group is None: return True

        user_permissions = user.get_user_permissions()
        group_permissions = group.permissions.annotate(
            permission_id_str=permission_id_str
        ).values_list('permission_id_str', flat=True)

        # user is member or has at least the group permissions
        return user.groups.filter(name=group.name).exists() or all(
            p in user_permissions
            for p in group_permissions
        )

    def has_view_permission(self, request, obj=None):
        return self._has_permissions(request.user, obj) and \
            super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return  self._has_permissions(request.user, obj) and \
            super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return self._has_permissions(request.user, obj) and \
            super().has_delete_permission(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'permissions' in form.base_fields:
            permissions = form.base_fields['permissions']
            user_permissions = request.user.get_user_permissions()
            permissions.queryset = permissions.queryset.annotate(
                permission_id_str=permission_id_str
            ).filter(permission_id_str__in=user_permissions)

        return form

    # TODO instead of has_*_permission
    # def get_queryset(self):
    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
    #     # filter (is_member or has_all_the_permissions)


