from .models import EmailNotificationSettings, get_users_with_permission
from django.core import mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from historical.models import Event


def send_message(message):
    settings = EmailNotificationSettings.load()
    if not settings.enabled:
        return

    users = get_users_with_permission("alerts.receive_alerts")

    with mail.get_connection(
        backend = "django.core.mail.backends.smtp.EmailBackend",
        host = settings.host,
        port = settings.port,
        username = settings.username,
        password = settings.password,
        use_tls = settings.use_tls,
        use_ssl = settings.use_ssl,
    ) as connection:
        email = mail.EmailMessage(
            subject=_("Alarmas App Instalaciones"),
            body=message,
            to=[user.email for user in users],
            connection=connection,
        ).send()