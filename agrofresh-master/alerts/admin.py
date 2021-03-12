from . import models
from . import email
from . import telegram
from core.admin import ReadOnlyMixin, SingletonMixin
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _


class SendTestMessageMixin(admin.ModelAdmin):
    def send_message(self, message):
        # TODO send_message in NotificationSettings?
        raise NotImplementedError()

    def response_change(self, request, obj):
        if "send-test-message" in request.POST:
            # obj : NotificationSettings
            self.send_message(_("This is just a test message, please ignore."))
            self.message_user(request, _("Test message sent"))
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)


@admin.register(models.EmailNotificationSettings)
class EmailNotificationSettingsAdmin(SingletonMixin, SendTestMessageMixin, admin.ModelAdmin):
    change_form_template = "email_settings_changeform.html"

    def send_message(self, message):
        email.send_message(message)


@admin.register(models.TelegramNotificationSettings)
class TelegramNotificationSettingsAdmin(SingletonMixin, SendTestMessageMixin, admin.ModelAdmin):
    change_form_template = "telegram_settings_changeform.html"

    def send_message(self, message):
        telegram.send_message(message)

