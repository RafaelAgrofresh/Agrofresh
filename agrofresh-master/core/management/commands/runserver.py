import uvicorn
import re
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.runserver import naiveip_re
from django.core.management.color import supports_color
from urllib.parse import urlparse
from core.settings import ASGI_APPLICATION, DEBUG
from core.signals import app_start, app_stop

# try:
#     import colorama
# except ImportError:
#     HAS_COLOR_SUPPORT = supports_color()
# else:
#     colorama.init()
#     HAS_COLOR_SUPPORT = True
HAS_COLOR_SUPPORT = supports_color()


class Command(BaseCommand):
    help = 'Starts a uvicorn ASGI server Web server.'
    default_addr = '127.0.0.1'
    default_addr_ipv6 = '::1'
    default_port = '8000'

    def add_arguments(self, parser):
        parser.add_argument(
            'addrport', nargs='?',
            help='Optional port number, or ipaddr:port'
        )
        parser.add_argument(
            '--no-reload', action='store_false', dest='use_reloader',
            help='enable auto-reload.',
        )

    def handle(self, *args, **options):
        log_levels = "critical|error|warning|info|debug|trace".split('|')
        verbosity = options['verbosity'] + 2
        verbosity = max(0, min(verbosity, len(log_levels) - 1))
        addrport = options['addrport'] or f"{self.default_addr}:{self.default_port}"
        use_reloader = options['use_reloader']
        colorize = (
            options['force_color']
            or HAS_COLOR_SUPPORT and not options['no_color']
        )

        m = re.match(naiveip_re, addrport)
        if not m:
            raise CommandError(f'"{addrport}" is not a valid port number or address:port pair.')

        addr, _ipv4, _ipv6, _fqdn, port = m.groups()
        if not port.isdigit():
            raise CommandError(f"{port} is not a valid port number.")

        config = {
            "host" : _ipv4 or _ipv6 or _fqdn,
            "port" : int(port),
            "log_level" : log_levels[verbosity],
            "reload": use_reloader,
            "use_colors": colorize,
        }

        if DEBUG:
            print("(security.W018) You should not have DEBUG set to True in deployment!")

        app_start.send(sender=self.__class__)
        uvicorn.run(ASGI_APPLICATION, **config)
        app_stop.send(sender=self.__class__)
