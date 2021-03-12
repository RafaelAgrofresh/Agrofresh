from django.contrib.auth.decorators import user_passes_test, REDIRECT_FIELD_NAME
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_noop as _
from .models import get_read_permission, get_write_permission, CommsPermissions
from .structs import DataStruct


def get_tags_permissions(*tags, readonly=False):
    def tag_permissions(tag):
        yield get_read_permission(tag)

        if not readonly:
            yield get_write_permission(tag)

    content_type = ContentType.objects.get_for_model(CommsPermissions)
    permissions = [
        Permission.objects.get_or_create(
            codename=name,
            name=description,
            content_type=content_type,
        )
        for tag in tags
        for name, description in tag_permissions(tag)
    ]
    return permissions


def get_auth_permissions():
    # permissions = [
    #     'auth.add_group',
    #     'auth.add_permission',
    #     'auth.add_user',
    #     'auth.change_group',
    #     'auth.change_permission',
    #     'auth.change_user',
    #     'auth.delete_group',
    #     'auth.delete_permission',
    #     'auth.delete_user',
    #     'auth.view_group',
    #     'auth.view_permission',
    #     'auth.view_user',
    # ]
    # permissions = [p.split('.') for p in permissions]
    # permissions = [
    #     Permission.objects.get(
    #         content_type__app_label=app,
    #         codename=codename)
    #         for app, codename in permissions
    # ]
    # return permissions
    # FIXME django.contrib.auth.models.DoesNotExist: Permission matching query does not exist
    return []

PERMISSIONS = {
    'read_all':                get_tags_permissions(*DataStruct.get_tags(), readonly=True),
    'modos de funcionamiento': get_tags_permissions('operation'),
    'habilitados':             get_tags_permissions('enabled'),
    'reset alarmas':           get_tags_permissions('reset_alarm'),
    'consignas':               get_tags_permissions('set_point'),
    'datos':                   get_tags_permissions('data'),
    'forzados':                get_tags_permissions('forced'),
    'configuracion':           get_tags_permissions('settings'),
    'crear usuarios':          get_auth_permissions(),
}

class PredefinedGroups:
    GROUPS = [
        {
            'name': 'Nivel1',
            'permissions': [
                *PERMISSIONS.get('read_all'),
            ]
        },
        {
            'name': 'Nivel2',
            'permissions': [
                *PERMISSIONS.get('read_all'),
                *PERMISSIONS.get('modos de funcionamiento'),
                *PERMISSIONS.get('habilitados'),
                *PERMISSIONS.get('reset alarmas'),
            ]
        },
        {
            'name': 'Nivel3',
            'permissions': [
                *PERMISSIONS.get('read_all'),
                *PERMISSIONS.get('modos de funcionamiento'),
                *PERMISSIONS.get('habilitados'),
                *PERMISSIONS.get('reset alarmas'),
                *PERMISSIONS.get('consignas'),
                *PERMISSIONS.get('datos'),
            ]
        },
        {
            'name': 'Nivel4',
            'permissions': [
                *PERMISSIONS.get('read_all'),
                *PERMISSIONS.get('modos de funcionamiento'),
                *PERMISSIONS.get('habilitados'),
                *PERMISSIONS.get('reset alarmas'),
                *PERMISSIONS.get('consignas'),
                *PERMISSIONS.get('datos'),
                *PERMISSIONS.get('forzados'),
                *PERMISSIONS.get('configuracion'),
            ]
        },
        {
            'name': 'Nivel5',
            'permissions': [
                *PERMISSIONS.get('read_all'),
                *PERMISSIONS.get('modos de funcionamiento'),
                *PERMISSIONS.get('habilitados'),
                *PERMISSIONS.get('reset alarmas'),
                *PERMISSIONS.get('consignas'),
                *PERMISSIONS.get('datos'),
                *PERMISSIONS.get('forzados'),
                *PERMISSIONS.get('configuracion'),
                *PERMISSIONS.get('crear usuarios'),
            ]
        },
    ]

    @classmethod
    def create(cls):
        for group_def in cls.GROUPS:
            permissions = [p for p, _ in group_def.get('permissions')]
            group, created = Group.objects.get_or_create(name=group_def.get('name'))
            group.permissions.clear()
            group.permissions.set(permissions)


    @classmethod
    def delete(cls):
        for group_def in cls.GROUPS:
            group = Group.objects.get(name=group_def.get('name'))
            group.delete()


def user_is_member_of(group_name, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    # Check membership (TODO use @permission_required decorator instead)
    # Usage:
    #   @user_is_member_of('level1')
    #   def view....
    test_func = lambda user: user.groups.filter(name=group_name).exists()
    return user_passes_test(test_func, login_url, redirect_field_name)
