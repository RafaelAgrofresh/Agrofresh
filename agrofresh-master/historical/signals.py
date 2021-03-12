from django.dispatch import receiver
from django.utils import timezone
import django.dispatch
import logging


model_change = django.dispatch.Signal(providing_args=['model'])
logger = logging.getLogger(__name__)


@receiver(model_change)
def model_change_event(sender, model, **kwargs):
    logger.info(f"model change @ {model}")

