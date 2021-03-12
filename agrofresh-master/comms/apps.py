from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from core import settings
import asyncio

class Config(AppConfig):
    name = 'comms'
    verbose_name = _('Communications')

    def ready(self):
        from .tasks import mbus
        loop = asyncio.get_event_loop()
        loop.create_task(mbus(period=settings.COMMS_TASK_PERIOD))
