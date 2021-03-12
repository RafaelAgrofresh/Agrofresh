from django.apps import AppConfig
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class Config(AppConfig):
    name = 'historical'
    verbose_name = _('Historical data')

    def ready(self):
        site = HistoricalAdminSite()
        admin.site = site
        admin.sites.site = site


class HistoricalAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            "Measurements": 1,
            "Alarms": 2,
            "Parameters": 3,
            "Events": 4
        }
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering.get(x['name'], 0))

        return app_list

