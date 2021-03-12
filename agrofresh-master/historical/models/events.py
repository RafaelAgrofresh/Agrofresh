from dataclasses import dataclass
from datetime import datetime
from django.db import connection, models
from django.core import exceptions
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from comms.structs import DataStruct
from cold_rooms.models import ColdRoom
from core.models import (
    Named, Described, Enablable, Timestamped, Typed,
)
from core.models.mixins import (
    InheritanceParentMixin, SaveOnValueChangeMixin,
)
from .mixins import StructLookUpTableMixin
import logging


logger = logging.getLogger(__name__)


# TODO sql RunSQL mgration operation
# https://schinckel.net/2020/03/03/postgres-view-from-django-queryset/
# https://schinckel.net/2016/04/30/multi-table-inheritance-and-the-django-admin/

class Alarm(StructLookUpTableMixin, Named, Enablable):
    # FIXME broken
    # def events_count(self):
    #     return self.alarm_events.count()

    @classmethod
    def update(cls):
        # TODO remove alarms not in DataStruct
        count = 0
        for field in DataStruct.alarm_fields:
            alarm, created = Alarm.objects.get_or_create(
                name=field.metadata.get('path'),
            )

            if created:
                alarm.save()
                count += 1

        return count

    class Meta:
        verbose_name = _("Alarm")
        verbose_name_plural = _("Alarms")

    def __str__(self):
        return str(_(self.description))


class Parameter(StructLookUpTableMixin, Named, Typed, Enablable):
    # FIXME broken
    # def events_count(self):
    #     return self.parameter_change_events.count()

    # Parameters LUT
    @classmethod
    def update(cls):
        # TODO remove paramters not in DataStruct
        count = 0
        for field in DataStruct.parameter_fields:
            # TODO debug
            # field_type = Typed.Type.from_type(field.type)
            # if field_type == Typed.Type.__empty__:
            #     print(f"field '{field.name}' type '{field.type}' not found")
            param, created = Parameter.objects.get_or_create(
                name=field.metadata.get('path'),
                type=Typed.Type.from_type(field.type),
            )

            if created:
                param.save()
                count += 1

        return count

    class Meta:
        verbose_name = _("Parameter")
        verbose_name_plural = _("Parameters")

    def __str__(self):
        return str(_(self.description))

class Event(InheritanceParentMixin, SaveOnValueChangeMixin, Timestamped):
    type = models.CharField(max_length=28)
    meta = models.JSONField(null=True)
    value = models.JSONField(null=True)

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ('-ts','id')
        get_latest_by = 'ts'
        # unique_together = [('ts', 'type', 'meta')]
        indexes = [
            models.Index(fields=['-ts', 'id'], name='%(app_label)s_%(class)s_idx')
            # TODO test BrinIndex(fields=['-ts', 'id'])
            #   https://hakibenita.com/9-django-tips-for-working-with-databases
            #   ERROR: brin does not support ASC/DESC options
        ]

    lut = {
        'cold_rooms': ColdRoom.objects.all(),
        'alarms': Alarm.objects.all(),
        'parameters': Parameter.objects.all(),
    }

    def foreign_keys(self):
        # TODO move to Event classes
        def next_or_none(iterator):
            try:
                return next(iterator)
            except StopIteration:
                return None

        references = []
        if 'cold_room' in self.meta:
            pk = self.meta.get('cold_room')
            cold_room = next_or_none(c for c in self.lut['cold_rooms'] if c.id == pk)
            references.append(cold_room)

        if 'alarm' in self.meta:
            pk = self.meta.get('alarm')
            alarm = next_or_none(a for a in self.lut['alarms'] if a.id == pk)
            references.append(alarm)

        if 'parameter' in self.meta:
            pk = self.meta.get('parameter')
            parameter = next_or_none(p for p in self.lut['parameters'] if p.id == pk)
            references.append(parameter)

        if 'user' in self.meta:
            user = self.meta.get('user')
            references.append(user)

        if 'ip' in self.meta:
            from ipaddress import ip_address
            ip = self.meta.get('ip')
            references.append(ip_address(ip))

        return references

    def description(self):
        # TODO DRY EventDescriptionMixin
        # TODO Refactor use proxy models implementing description
        links = []
        for ref in self.foreign_keys():
            try:
                if isinstance(ref, (Alarm, Parameter)):
                    links.append(('#', str(ref.description) or '--'))
                elif hasattr(ref, "name"):
                    links.append(('#', str(ref.name) or '--'))
                else:
                    links.append(('#', str(ref)))
            except Exception as error:
                print(f"ERROR:: {ref} throws {error}")
                # removed or renamed variable
                links.append(('#', str(ref)))

        display_text = ', '.join(display for (link, display) in links)
        return display_text if display_text else "--"

    description.verbose_name=_('description')
    description.help_text=_('description help text')
    description = property(description)

    def get_cache_key(self):
        return (self.__class__, self.type, *self.meta.items())

    def get_latest_value(self):
        try:
            latest = Event.objects.filter(type=self.type, meta=self.meta).latest()
            return latest.value
        except (exceptions.ObjectDoesNotExist, self.DoesNotExist):
            return None

    # class Manager(models.Manager):
    #     def get_unacknowledged_alarms(self):
    #         return self.get_annotated_alarms().filter(ack=False)

    #     def get_annotated_alarms(self):
    #         ts_end = (
    #             # Given an alarm event select the related deactivation
    #             self.filter(
    #                 ts__gt=models.OuterRef("ts"),
    #                 type=AlarmEvent.__name__, value=False,
    #                 meta=models.OuterRef("meta"),
    #             )
    #             .annotate(min_ts=models.Min("ts"))
    #             .values('min_ts')
    #         )
    #         ts_ack = (
    #             # Given an alarm event select the most recent ack event
    #             self.filter(
    #                 models.Q(ts__gt=models.OuterRef("ts"))
    #                 & models.Q(type=AcknowledgeAlarmsEvent.__name__)
    #                 & (
    #                     models.Q(meta__cold_room=models.OuterRef("meta__cold_room"))
    #                     | models.Q(meta__cold_room__isnull=True)
    #                 )
    #             )
    #             .annotate(min_ts=models.Min("ts"))
    #             .values('min_ts')
    #         )

    #         return (
    #             # select alarm activations
    #             self.filter(type=AlarmEvent.__name__, value=True)
    #             .annotate(
    #                 # annotate with related deactivation ts
    #                 ts_end=models.Subquery(ts_end[:1]),
    #                 # annotate with related ack ts
    #                 temp_ack=models.Subquery(ts_ack[:1]),
    #             )
    #             # .extra?
    #             .annotate(
    #                 # annotate with alarm active flag
    #                 active=models.Case(
    #                     models.When(ts_end__isnull=True, then=models.Value(True)),
    #                     default=models.Value(False),
    #                     output_field=models.BooleanField(),
    #                 ),
    #                 # annotate with alarm ack flag
    #                 ack=models.Case(
    #                     models.When(
    #                         ts_end__lt=models.F('temp_ack'),
    #                         then=models.Value(True)
    #                     ),
    #                     default=models.Value(False),
    #                     output_field=models.BooleanField(),
    #                 ),
    #                 # add ts_ack only if ts_ack > ts_end
    #                 ts_ack=models.Case(
    #                     models.When(
    #                         ts_end__lt=models.F('temp_ack'),
    #                         then=models.F('temp_ack')
    #                     ),
    #                     default=models.Value(None),
    #                     output_field=models.DateTimeField(),
    #                 )
    #             )
    #             .order_by('-ts')
    #         )

    class AlarmsManager(models.Manager):
        def get_unacknowledged_alarms(self):
            return self.raw("""
            with annotated as (
                select
                    *, (
                        -- Select related alarm deactivation ts
                        select min(ts)
                        from historical_event
                        where type = 'AlarmEvent'
                        and meta = e.meta
                        and value = 'false'::jsonb
                        and ts > e.ts
                    ) as ts_end,
                    (
                        -- Select related alarm ack ts
                        select min(ts)
                        from historical_event
                        where type = 'AcknowledgeAlarmsEvent'
                        and (meta->'cold_room' is null or meta->'cold_room' = e.meta->'cold_room')
                        and ts > (
                            -- Select related alarm deactivation ts
                            select min(ts)
                            from historical_event
                            where type = 'AlarmEvent'
                            and meta = e.meta
                            and value = 'false'::jsonb
                            and ts > e.ts
                        )
                    ) as ts_ack
                from historical_event e
                where type = 'AlarmEvent'
                and value = 'true'::jsonb
            )
            select
                *,
                (ts_end is null) as active,
                (ts_ack is not null) as ack
            from annotated
            where ts_ack is null
            order by ts desc
            """)

        def get_annotated_alarms(self):
            return self.raw("""
            with annotated as (
                select
                    *, (
                        -- Select related alarm deactivation ts
                        select min(ts)
                        from historical_event
                        where type = 'AlarmEvent'
                        and meta = e.meta
                        and value = 'false'::jsonb
                        and ts > e.ts
                    ) as ts_end,
                    (
                        -- Select related alarm ack ts
                        select min(ts)
                        from historical_event
                        where type = 'AcknowledgeAlarmsEvent'
                        and (meta->'cold_room' is null or meta->'cold_room' = e.meta->'cold_room')
                        and ts > (
                            -- Select related alarm deactivation ts
                            select min(ts)
                            from historical_event
                            where type = 'AlarmEvent'
                            and meta = e.meta
                            and value = 'false'::jsonb
                            and ts > e.ts
                        )
                    ) as ts_ack
                from historical_event e
                where type = 'AlarmEvent'
                and value = 'true'::jsonb
            )
            select
                *,
                (ts_end is null) as active,
                (ts_ack is not null) as ack
            from annotated
            order by ts desc
            """)

        def remove_orphaned_events(self):
            # TODO find and remove events with non existing cold_room id
            raise NotImplementedError()

    class ParametersManager(models.Manager):
        def get_latest_settings(self, cold_room=None, working_mode=None):
            if not isinstance(cold_room, int): raise Exception("expected cold_room:int")
            if not isinstance(working_mode, bool): raise Exception("expected working_mode:bool")

            return self.raw("""
            -- get latest parameter values for a given workingMode
            -- get last ts for evt where workingMode = value as last_ts
            -- get ts for evt where workingMode != value and ts > last_ts as until_ts
            -- distinct on (meta) for evt where ts < until_ts
            with annotated as (
                select
                    *,
                    (
                        select max(ts)
                        from historical_event
                        where type = 'ParameterChangeEvent'
                            and (meta->'cold_room')::integer = %(cold_room)s
                            and (meta->'parameter')::integer = (
                                select id from historical_parameter where name = 'workingMode'
                            )
                            and value = (case when %(working_mode)s then 'true' else 'false' end)::jsonb
                    ) as ts_last
                from historical_event
                where type = 'ParameterChangeEvent'
                    and (meta->'cold_room')::integer = %(cold_room)s
                    and (meta->'parameter')::integer in (
                        select id from historical_parameter
                        where name in (
                            'workingMode',
                            'refTemperature',
                            'refHumidity',
                            'highRefCO2',
                            'lowRefCO2',
                            'refC2H4'
                        )
                    )
                order by ts desc
            )
            select
                distinct on (meta)
                *
            from annotated
            where ts >= ts_last
                and ts < (
                    select coalesce(min(ts), now())
                    from historical_event
                    where type = 'ParameterChangeEvent'
                        and (meta->'cold_room')::integer = %(cold_room)s
                        and (meta->'parameter')::integer = (
                            select id from historical_parameter where name = 'workingMode'
                        )
                        and value != (case when %(working_mode)s then 'true' else 'false' end)::jsonb
                        and ts > ts_last
                );
            """, {
                'cold_room' : cold_room,
                'working_mode' : working_mode,
            })

    objects = models.Manager()
    alarms  = AlarmsManager()
    params  = ParametersManager()


@dataclass
class BaseEvent:
    ts: datetime = None

    def to_dict(self):
        return {
            'ts' : self.ts or timezone.now(),
            'type': self.__class__.__name__,
        }

    @classmethod
    def from_event(cls, event):
        assert event.type == cls.__name__
        return cls.from_dict(**{
            'ts': event.ts,
            **event.data,
        })

    @classmethod
    def from_dict(cls, **kwargs):
        raise NotImplementedError()

    def to_event(self):
        data = self.to_dict()
        ts = data.pop('ts')
        type = data.pop('type')
        value = data.pop('value')
        return Event(ts=ts, type=type, meta=data, value=value)

    def save(self):
        event = self.to_event()
        event.save()


@dataclass
class AlarmEvent(BaseEvent):
    cold_room : ColdRoom = None
    alarm : Alarm = None
    value : bool = False

    def to_dict(self):
        return {
            **super().to_dict(),
            'cold_room' : self.cold_room.pk,
            'alarm' : self.alarm.pk,
            'value' : self.value,
        }

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**{
            **kwargs,
            'cold_room' : ColdRoom.objects.get(pk=kwargs.get('cold_room')),
            'alarm' : Alarm.objects.get(pk=kwargs.get('alarm')),
        })


@dataclass
class AcknowledgeAlarmsEvent(BaseEvent):
    cold_room : ColdRoom = None
    user : str = None

    def to_dict(self):
        import uuid
        data = {
            **super().to_dict(),
            'user': self.user,
            'value': str(uuid.uuid4()), # FIXME SaveOnlyOnValueChange
        }

        if self.cold_room is not None:
            data = { **data, 'cold_room' : self.cold_room.pk }

        return data

    @classmethod
    def from_dict(cls, **kwargs):
        if 'cold_room' in kwargs:
            kwargs = {
                **kwargs,
                'cold_room' : ColdRoom.objects.get(pk=kwargs.get('cold_room')),
            }
        return cls(**kwargs)


@dataclass
class AuthEvent(BaseEvent):
    user : str = None
    value : str = None
    ip : str = None

    class Type(models.TextChoices):
        logged_in    = 'logged_in',    _('logged in')
        logged_out   = 'logged_out',   _('logged out')
        login_failed = 'login_failed', _('login failed')

    def to_dict(self):
        data = {
            **super().to_dict(),
            'user' : self.user,
            'value' : self.value,
        }
        if self.ip is not None:
            data = { **data, 'ip': self.ip }

        return data

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**kwargs)


@dataclass
class ParameterChangeEvent(BaseEvent):
    cold_room : ColdRoom = None
    parameter : Parameter = None
    value : object = None

    def to_dict(self):
        return {
            **super().to_dict(),
            'cold_room' : self.cold_room.pk,
            'parameter' : self.parameter.pk,
            'value' : self.value,
        }

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**{
            **kwargs,
            'cold_room' : ColdRoom.objects.get(pk=kwargs.get('cold_room')),
            'parameter' : Parameter.objects.get(pk=kwargs.get('parameter')),
        })


@dataclass
class ParameterChangeCommand(ParameterChangeEvent):
    user : str = None

    def to_dict(self):
        return {
            **super().to_dict(),
            'user' : self.user,
        }

    @classmethod
    def from_dict(cls, **kwargs):
        return cls(**kwargs)


# class AlarmEvent(Event): # SaveOnValueChangeMixin
#     def __init__(self, *args, **kwargs):
#         if not 'ts' in kwargs:
#             id_, ts = args
#             data  = kwargs
#         else:
#             ts = kwargs.pop('ts')
#             data = {
#                 'cold_room': kwargs.pop('cold_room').name,
#                 'alarm': kwargs.pop('alarm').name,
#                 'value': kwargs.pop('value'),
#             }
#         super().__init__(**{ 'ts': ts, 'data': data })


#     def cold_room(self) -> ColdRoom:
#         return self.data.get('cold_room')

#     cold_room.verbose_name=_('cold_room')
#     cold_room.help_text=_('cold_room help text')
#     cold_room = property(cold_room)

#     def alarm(self) -> Alarm:
#         return self.data.get('cold_room')

#     alarm.verbose_name=_('alarm')
#     alarm.help_text=_('alarm help text')
#     alarm = property(alarm)

#     def value(self) -> bool:
#         return self.data.get('value')

#     value.verbose_name=_('value')
#     value.help_text=_('value help text')
#     value = property(value)

#     def description(self):
#         return _("'%(alarm)s' set to %(value)s") % {
#             'alarm': self.alarm.description,
#             'value': 'ON' if self.value  else 'OFF',
#         }
#     description.verbose_name=_('description')
#     description.help_text=_('description help text')
#     description = property(description)

#     class Meta:
#         proxy = True
#         verbose_name = _('alarm event')
#         verbose_name_plural = _('alarm events')
#         ordering = ('-ts', 'data__cold_room__name', 'data__alarm__name')
#         get_latest_by = 'ts'

#     # def get_cache_key(self):
#     #     return (self.__class__, self.cold_room.pk, self.alarm.pk)

#     # def get_latest_value(self):
#     #     return (AlarmEvent.objects
#     #         .filter(cold_room__pk=self.cold_room.pk, alarm__pk=self.alarm.pk)
#     #         .order_by('-ts')
#     #         .values('value')
#     #         .first())


# class AuthEvent(Event):
#     def __init__(self, *args, **kwargs):
#         ts = kwargs.pop('ts')
#         data = {
#             'user': kwargs.pop('user'),
#             'type': kwargs.pop('type'),
#         }
#         super().__init__(*args, **{ 'ts': ts, 'data': data })


#     def user(self) -> User:
#         return self.data('user')

#     user.verbose_name=_('user')
#     user.help_text=_('user help text')
#     user = property(user)

#     class Type(models.TextChoices):
#         logged_in    = 'logged_in',  _('logged in')
#         logged_out   = 'logged_out',   _('logged out')
#         login_failed = 'login_failed', _('login failed')

#     def type(self) -> Type:
#         return self.data('type')

#     type.verbose_name=_('type')
#     type.help_text=_('type help text')
#     type = property(type)

#     def description(self):
#         return _("User '%(user)s' %(type)s") % {
#             'user': self.user,
#             'type': self.type,
#         }
#     description.verbose_name=_('description')
#     description.help_text=_('description help text')
#     description = property(description)

#     class Meta:
#         proxy = True
#         verbose_name = _('auth event')
#         verbose_name_plural = _('auth events')
#         ordering = ('-ts', 'data__user')
#         get_latest_by = 'ts'


# class ParameterChangeEvent(Event): # SaveOnValueChangeMixin
#     def __init__(self, *args, **kwargs):
#         ts = kwargs.pop('ts')
#         data = {
#             'cold_room': kwargs.pop('cold_room').name,
#             'parameter': kwargs.pop('parameter').name,
#             'value': kwargs.pop('value'),
#         }
#         super().__init__(*args, **{ 'ts': ts, 'data': data })


#     def cold_room(self) -> ColdRoom:
#         return self.data.get('cold_room')

#     cold_room.verbose_name=_('cold_room')
#     cold_room.help_text=_('cold_room help text')
#     cold_room = property(cold_room)

#     def parameter(self) -> Parameter:
#         return self.data.get('parameter')

#     parameter.verbose_name=_('parameter')
#     parameter.help_text=_('parameter help text')
#     parameter = property(parameter)

#     def value(self) -> object:
#         return self.data.get('value')

#     value.verbose_name=_('value'),
#     value.help_text=_('value help text')
#     value = property(value)

#     def description(self):
#         return _("'%(param)s' set to %(value)s") % {
#             'param': self.parameter.description,
#             'value': self.value,
#         }

#     description.verbose_name=_('description')
#     description.help_text=_('description help text')
#     description = property(description)

#     class Meta:
#         proxy = True
#         verbose_name = _('parameter change event')
#         verbose_name_plural = _('parameter change events')
#         ordering = ['-ts', 'data__cold_room__name', 'data__parameter__name']
#         get_latest_by = 'ts'

#     # def get_cache_key(self):
#     #     return (self.__class__, self.cold_room.pk, self.parameter.pk)

#     # def get_latest_value(self):
#     #     return (ParameterChangeEvent.objects
#     #         .filter(cold_room__pk=self.cold_room.pk, parameter__pk=self.parameter.pk)
#     #         .order_by('-ts')
#     #         .values('value')
#     #         .first())


@receiver(user_logged_in)
def user_logged_in_handler(sender, user, **kwargs):
    logger.info(f"user '{user.username}' logged in")
    request = kwargs.get('request')
    ip_addr = request.META.get('REMOTE_ADDR')
    event = AuthEvent(
        ts=timezone.now(),
        value=AuthEvent.Type.logged_in,
        user=user.username,
        ip=ip_addr,
    )
    event.save()

@receiver(user_logged_out)
def user_logged_out_handler(sender, user, **kwargs):
    logger.info(f"user '{user.username}' logged out")
    request = kwargs.get('request')
    ip_addr = request.META.get('REMOTE_ADDR')
    event = AuthEvent(
        ts=timezone.now(),
        value=AuthEvent.Type.logged_out,
        user=user.username,
        ip=ip_addr,
    )
    event.save()

@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, **kwargs):
    logger.info(f"user {kwargs} failed logged attempt")
    username = credentials['username']
    request = kwargs.get('request')
     # TODO {'signal': ..., 'request': None}
    ip_addr = request.META.get('REMOTE_ADDR') if request else None
    event = AuthEvent(
        ts=timezone.now(),
        value=AuthEvent.Type.login_failed,
        user=username,
        ip=ip_addr,
    )
    event.save()

