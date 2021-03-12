from django.core.management.base import BaseCommand, CommandError
from alerts.models import TelegramNotificationSettings
from alerts.telegram import get_bot_info, get_updates


class Command(BaseCommand):
    help = 'Get telegram bot updates.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-n', '--news-only', action='store_true', dest='news_only',
            help='Show non registered chat IDs only.',
        )
        parser.add_argument(
            '--add', action='store_true', dest='add_chat_id',
            help='Add new chat IDs to receivers.',
        )

    def handle(self, *args, **options):
        news_only = options['news_only']
        add_chat_id = options['add_chat_id']

        settings = TelegramNotificationSettings.load()
        bot_info = get_bot_info(settings)
        print(f"[i] Bot name @{bot_info.get('username')}")

        registered_ids = set(
            int(chat_id.strip())
            for chat_id in settings.receivers.split()
        )
        updates = [
            {
                **update,
                "registered" : update.get("chat_id") in registered_ids
            }
            for update in get_updates(settings)
        ]
        updates = [
            update for update in updates
            if not news_only or not update["registered"]
        ]

        for update in updates:
            chat_id = update.get("chat_id")
            first_name = update.get("first_name")
            text = update.get("text")
            registered = update.get("registered")
            print(f"chat_id:{chat_id} registered:{registered} first_name:{first_name} text:{text}")

        if not updates:
            print("[i] No incoming updates")

        elif updates:
            chat_ids = set(update["chat_id"] for update in updates)
            new_ids = set(chat_id for chat_id in chat_ids if chat_id not in registered_ids)
            print(f"[i] {len(updates)} incoming updates from {len(chat_ids)} unique IDs {chat_ids}")

            if new_ids:
                print(f"[i] Found {len(new_ids)} new IDs {new_ids}")

            if add_chat_id and new_ids:
                settings.receivers = '\n'.join(
                    str(chat_id)
                    for chat_id in registered_ids | new_ids
                )
                settings.save()
                print(f"[i] Added {len(new_ids)} new IDs {new_ids}")
