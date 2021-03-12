from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import asyncio


class Config(AppConfig):
    name = 'alerts'
    verbose_name = _('Alert notifications')

    # When an alert changes state, it sends out notifications.
    # An alert rule can have multiple notifications.
    # A notification defines a template and the notification channel (email, telegram, ...).

    def ready(self):
        from . import signals
        from . import notifier
        signals.notifications.subscribe(
            notifier.Notifier()
        )
