from . import email
from . import telegram
import logging
import rx


logger = logging.getLogger(__name__)


class Notifier(rx.core.typing.Observer):
    def __init__(self):
        logger.info(f"{self}: created")

    def on_next(self, value):
        if isinstance(value, list):
            value = '\n'.join(value)

        logger.info(f"{self}: next -> {value}")
        telegram.send_message(value)
        email.send_message(value)

    def on_error(self, error):
        logger.error(f"{self}: error -> {error}")

    def on_completed(self):
        logger.info(f"{self}: done!")

    def __str__(self):
        return f"{self.__class__.__name__}_{hex(id(self))}"