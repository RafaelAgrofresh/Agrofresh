from core.models import SingletonModel
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models.base import Sortable
from .measurements import Measurement


class Settings(SingletonModel):
    show_unack_alarms = models.BooleanField(
        default=True,
        verbose_name = _("Show unacknowledged alarms"),
        help_text= _("Show unacknowledged and active alarms, or only active"),
    )
    default_measurements = models.ManyToManyField(
        Measurement,
        verbose_name = _("Default historical measurements"),
        help_text= _("List of measurements to include by default in historical data view"),
        through='SortedMeasurementsList',
        through_fields=('settings', 'measurement'),
    )

    class Meta:
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")


class SortedMeasurementsList(Sortable, models.Model):
    settings = models.ForeignKey(Settings, on_delete=models.CASCADE)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE)

    class Meta:
        ordering = (*Sortable.Meta.ordering,)
        verbose_name = _("measurement")
        verbose_name_plural = _("measurements")
        # enforce uniqueness on the (settings, measurement) pair
        unique_together = [('settings', 'measurement')]

    # objects = Sortable.Manager()

    def __str__(self):
        return f'#{self.sort_order} - {self.measurement}'
