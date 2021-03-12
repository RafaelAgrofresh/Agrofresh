from django.core.management.base import BaseCommand
import logging


class Command(BaseCommand):
    help = 'Get a list of all the loggers available in the system.'

    def handle(self, *args, **options):
        loggers = {
            name: logging.getLogger(name)
            for name in sorted(logging.root.manager.loggerDict)
            # if 'django' in name
        }

        for name, logger in loggers.items():
            print(
                f'Logger Name: {name}\n'
                f'       Handlers: {logger.handlers}\n'
                f'       Propagates: {logger.propagate}\n'
            )
