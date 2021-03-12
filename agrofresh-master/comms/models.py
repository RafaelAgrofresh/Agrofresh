from django.db import models
from django.utils.translation import gettext_noop as _
from .structs import DataStruct


def get_read_permission(tag):
    return (
        f'can_read_vars_tagged_as_{tag}',
        _('Can read variables tagged as %(tag)s') % { 'tag': tag }
    )

def get_write_permission(tag):
    return (
        f'can_write_vars_tagged_as_{tag}',
        _('Can write variables tagged as %(tag)s')  % { 'tag': tag }
    )


class CommsPermissions(models.Model):
    # Custom permissions holder class
    #
    # Usage:
    #   @permission_required('comms.can_read_vars_tagged_as_something')
    #   request.user.has_perm('comms.can_read_vars_tagged_as_something')
    #   {% if perms.comms.can_read_vars_tagged_as_something %}

    class Meta:
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model.

        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        permissions = [
            # tagged fields access permissions
            permission
            for tag in sorted(DataStruct.get_tags())
            for permission in [
                get_read_permission(tag),
                get_write_permission(tag),
            ]
        ]


class ViewsPermissions(models.Model):
    # Custom permissions holder class
    #
    # Usage:
    #   @permission_required('comms.can_view_comms_data')
    #   request.user.has_perm('comms.can_view_comms_data')
    #   {% if perms.comms.can_view_comms_data %}

    class Meta:
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model.

        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        permissions = [
            ('can_view_comms_data', _('Can view communication data')),
            ('can_set_working_mode', _('Can set working mode')),
            ('can_acknowledge_alarms', _('Can acknowledge alarms')),
            ('can_accept_messages', _('Can accept messages')),
            ('can_export_memory_map', _('Can export memory map')),
        ]