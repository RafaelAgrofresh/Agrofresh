from django import forms
from django.contrib.auth.models import Permission, ContentType, User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import SingletonModel, Enablable


def get_permission_object(permission_str):
    app_label, code = app_label, codename = permission_str.split('.')
    return Permission.objects.filter(
        content_type__app_label=app_label,
        codename=codename
    ).first()


def get_users_with_permission(permission_str, include_su=True):
    permission_obj = get_permission_object(permission_str)
    q = models.Q(groups__permissions=permission_obj) | models.Q(user_permissions=permission_obj)

    if include_su:
        q |= models.Q(is_superuser=True)

    return User.objects.filter(q)


class AlertPermissions(models.Model):
    # Custom permissions holder class
    #
    # Usage:
    #   @permission_required('alert.receive_alerts')
    #   request.user.has_perm('alert.receive_alerts')
    #   {% if perms.alert.receive_alerts %}

    class Meta:
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model.

        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        permissions = [
            (f'receive_alerts', _('Receive alerts')),
        ]

    # @classmethod
    # def get_alert_permissions(cls):
    #     content_type = ContentType.objects.get_for_model(cls)
    #     permissions = [
    #         Permission.objects.get_or_create(
    #             codename=name,
    #             name=description,
    #             content_type=content_type,
    #         )
    #         for name, description in cls.Meta.permissions
    #     ]
    #     return permissions


class EmailNotificationSettings(SingletonModel, Enablable):
    username = models.CharField(max_length=250)         # EMAIL_HOST_USER
    password = models.CharField(max_length=250)         # EMAIL_HOST_PASSWORD
    host = models.CharField(
        max_length=250,
        default="localhost"
    )                                                   # EMAIL_HOST
    port = models.PositiveSmallIntegerField(            # EMAIL_PORT
        default=587,
        validators=[
            # MinValueValidator(1),
            MaxValueValidator(65535),
        ]
    )
    use_tls = models.BooleanField(default=True)         # EMAIL_USE_TLS
    use_ssl = models.BooleanField(default=False)        # EMAIL_USE_SSL

    class Meta:
        verbose_name = _("Email Notification Settings")
        verbose_name_plural = _("Email Notification Settings")


class TelegramNotificationSettings(SingletonModel, Enablable):

    api_token = models.CharField(
        max_length=250,
        # label=_('BotAPI token'),
        # widget=forms.TextInput(attrs={'placeholder': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}),
        help_text=_('Read more: https://core.telegram.org/bots/api#authorizing-your-bot'),
    )

    receivers = models.TextField(
        # label=_('Receivers'),
        # widget=forms.Textarea(attrs={'class': 'span6'}),
        blank=True,
        help_text=_('Enter receivers IDs (one per line).\nPersonal messages, group chats and channels also available.'),
    )

    class Meta:
        verbose_name = _("Telegram Notification Settings")
        verbose_name_plural = _("Telegram Notification Settings")
