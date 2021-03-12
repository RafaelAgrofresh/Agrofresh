from django.core.management.base import BaseCommand, CommandError
from historical.models import Measurement, Alarm, Parameter
from comms.structs import DataStruct


class Command(BaseCommand):
    help = 'Search for deleted or renamed variables.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-y', '--yes', action='store_true', dest='assume_yes',
            help='Automatic yes to prompts; assume "yes" as answer to all prompts and run non-interactively.',
        )
        parser.add_argument(
            '--rm', action='store_true', dest='remove_vars',
            help='Clean deleted or renamed variables.',
        )

    def handle(self, *args, **options):
        remove_vars = options['remove_vars']
        assume_yes = options['assume_yes']

        self.stdout.write(
            f"[+] Checking that defined variables correspond to {DataStruct.__class__.__name__} fields ..."
        )

        var_list = [
            *Measurement.objects.all(),
            *Alarm.objects.all(),
            *Parameter.objects.all(),
        ]

        found_cnt = 0
        deleted_cnt = 0
        for var in var_list:
            try:
                field = DataStruct.get_field(var.name)
            except Exception:
                self.stdout.write(
                    f"[i] {var.__class__.__name__} '{var.name}' not found in {DataStruct.__name__}"
                )
                found_cnt += 1

                if not remove_vars:
                    continue

                if not assume_yes:
                    confirmation = input(
                        f"[?] Would you like to remove {var.__class__.__name__} '{var.name}'? [y/N] "
                    ) or 'n'

                    if not confirmation.lower() in ['y', 'yes']:
                        continue

                var.delete()
                deleted_cnt += 1
                self.stdout.write(f"[!] {var.__class__.__name__} '{var.name}' deleted!" )

        self.stdout.write(f"[i] found {found_cnt} / deleted {deleted_cnt}")
