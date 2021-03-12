from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.management.commands.createsuperuser import get_user_model
from django.core.management import CommandError
from decouple import config


class Command(createsuperuser.Command):
    help = 'Crate a superuser, using the values provided'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        database = 'default' # config('DB_NAME', default=None)
        username = config('SU_USERNAME', default=None)
        password = config('SU_PASSWORD', default=None)
        email    = config('SU_EMAIL', default=None)

        if database is None:
            raise CommandError("DB_NAME env var required")

        if username is None:
            raise CommandError("SU_USERNAME env var required")

        if password is None:
            raise CommandError("SU_PASSWORD env var required")

        user_data = {
            'username': username,
            'password': password,
            'email': email,
        }
        self.UserModel._default_manager.db_manager(database).create_superuser(**user_data)
