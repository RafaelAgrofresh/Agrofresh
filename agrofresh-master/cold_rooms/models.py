from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Sortable, Named, Described


class ModbusTcpEndpoint(models.Model):
    host = models.GenericIPAddressField(
        default='127.0.0.1',
        verbose_name=_('ip address'),
        help_text=_('modbus slave ip address'))

    port = models.IntegerField(
        default=502,
        verbose_name=_('port'),
        help_text=_('tcp port number'),
        validators=[MinValueValidator(0), MaxValueValidator(2**16-1)])

    unit = models.IntegerField(
        default=0x00,
        verbose_name=_('unit identifier'),
        help_text=_('modbus slave unit identifier (255 if not used)'),
        validators=[MinValueValidator(0), MaxValueValidator(255)])

    @property
    def endpoint(self):
        return f"tcp://{self.host}:{self.port}/mbus?unit={self.unit}"

    # TODO convert to one-to-one relationship
    class Meta:
        abstract = True


class ModbusTcpAddress(ModbusTcpEndpoint):
    address = models.IntegerField(
        default=40001,
        verbose_name=_('base address'),
        help_text=_('data structure base address'))

    @property
    def endpoint(self):
        return f"{super().endpoint}&addr={self.address}"

    # TODO convert to one-to-one relationship
    # TODO make generic Address (many-to-one) EndPoint
    class Meta:
        abstract = True


class EnableableMeasurementsMixin(models.Model):
    enable_temperature_measurement = models.BooleanField(
        default=True,
        verbose_name=_('temperature measurement'),
        help_text=_('enables temperature measurement'))

    enable_humidity_measurement = models.BooleanField(
        default=True,
        verbose_name=_('humidity measurement'),
        help_text=_('enables humidity measurement'))

    enable_CO2_measurement = models.BooleanField(
        default=True,
        verbose_name=_('CO2 measurement'),
        help_text=_('enables CO2 measurement'))

    enable_C2H4_measurement = models.BooleanField(
        default=True,
        verbose_name=_('C2H4 measurement'),
        help_text=_('enables C2H4 measurement'))

    class Meta:
        abstract = True


class EnableableProportionalCtrl(models.Model):
    enable_CO2_proportional_ctrl = models.BooleanField(
        default=True,
        verbose_name=_('CO2 proportional control'),
        help_text=_('enables CO2 proportional control option'))

    enable_C2H4_proportional_ctrl = models.BooleanField(
        default=True,
        verbose_name=_('C2H4 proportional control'),
        help_text=_('enables C2H4 proportional control option'))

    class Meta:
        abstract = True


class ColdRoom(
    Sortable, Named, Described, ModbusTcpAddress,
    EnableableProportionalCtrl,
    EnableableMeasurementsMixin,
):
    enable_selector = models.BooleanField(
        default=True,
        verbose_name=_('Selector'),
        help_text=_('enables selector'))

    class Meta:
        verbose_name = _('cold room')
        verbose_name_plural = _('cold rooms')
        ordering = (*Sortable.Meta.ordering,) # 'name'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.__notify_model_change()

    def delete(self, using=None, keep_parents=False):
        self.__delete_measurement_data()
        super().delete(using, keep_parents)
        self.__notify_model_change()

    def __delete_measurement_data(self):
        # TODO improve, decouple cold_rooms <-> measurements
        from historical.models.measurements import BooleanData, FloatData, IntegerData
        BooleanData.objects.filter(cold_room=self).delete()
        FloatData.objects.filter(cold_room=self).delete()
        IntegerData.objects.filter(cold_room=self).delete()

    def __notify_model_change(self):
        from .signals import model_change
        model_change.send(sender=ColdRoom, model=self)

    # objects = Sortable.Manager()

    # TODO as Model Manager queries instead ?

    # @property
    # def parameters(self):
    #     # FIXME change to PostgreSQL and use distinct('name')
    #     from historical.models import Parameter
    #     return [
    #         self.parameter_change_events.filter(parameter__id=param.id).last()# FIXME .latest()
    #         for param in Parameter.objects.order_by('name').all()
    #     ]

    # @property
    # def alarms(self):
    #     # FIXME change to PostgreSQL and use distinct('name')
    #     from historical.models import Alarm
    #     return [
    #         self.alarm_events.filter(alarm__id=alarm.id).latest()
    #         for alarm in Alarm.objects.order_by('name').all()
    #     ]

    # @property
    # def active_alarms(self):
    #     # FIXME alarms QuerySet
    #     return [alarm for alarm in self.alarms if alarm.value]


class ViewsPermissions(models.Model):
    # Custom permissions holder class
    #
    # Usage:
    #   @permission_required('cold_rooms.can_view_cold_rooms_summary')
    #   request.user.has_perm('cold_rooms.can_view_cold_rooms_summary')
    #   {% if perms.cold_rooms.can_view_cold_rooms_summary %}

    class Meta:
        managed = False  # No database table creation or deletion  \
                         # operations will be performed for this model.

        default_permissions = () # disable "add", "change", "delete"
                                 # and "view" default permissions

        permissions = [
            ("can_view_cold_rooms_summary", _("Can view cold rooms summary")),
            ("can_view_cold_room_params", _("Can view cold room params")),
            ("can_view_cold_room_detail", _("Can view cold room detail")),
            ("can_edit_cold_room_control_options", _("Can edit cold room control options")),
        ]