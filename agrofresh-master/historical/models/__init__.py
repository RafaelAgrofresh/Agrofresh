from .settings import (
    Settings,
    SortedMeasurementsList,
)

from .events import (
    Event,
    AcknowledgeAlarmsEvent,
    AuthEvent,
    Alarm,
    AlarmEvent,
    Parameter,
    ParameterChangeEvent,
    ParameterChangeCommand,
)

from .measurements import (
    Measurement,
    FloatData,
    IntegerData,
    BooleanData,
    FloatDataDownsampled,
    IntegerDataDownsampled,
    MeasurementDataDownsampled,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class ViewsPermissions(models.Model):
    # Custom permissions holder class
    #
    # Usage:
    #   @permission_required('historical.receive_alerts')
    #   request.user.has_perm('historical.receive_alerts')
    #   {% if perms.historical.receive_alerts %}

    class Meta:
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model.

        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        permissions = [
            (f'can_view_historical_data', _('Can view historical data')),
            (f'can_view_events', _('Can view event')),
        ]


__all__ = [
    Event.__name__,
    AuthEvent.__name__,
    Alarm.__name__,
    AlarmEvent.__name__,
    Parameter.__name__,
    ParameterChangeEvent.__name__,
    Measurement.__name__,
    FloatData.__name__,
    IntegerData.__name__,
    BooleanData.__name__,
    FloatDataDownsampled.__name__,
    ViewsPermissions.__name__,
    Settings.__name__,
    SortedMeasurementsList.__name__,
]
