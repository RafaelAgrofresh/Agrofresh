from dataclasses import is_dataclass
from datetime import timedelta
from django import forms
from django.db import connection, models
from django.core import exceptions
from django.utils.translation import gettext_lazy as _
from core import settings
from comms.structs import DataStruct
from comms.mbus_types import MemMapped
from cold_rooms.models import ColdRoom
from core.models import (
    Named, Enablable, Timestamped, Typed,
)
from core.models.mixins import (
    classproperty, InheritanceParentMixin, SaveOnValueChangeMixin,
)
from .mixins import StructLookUpTableMixin
from . import table_function as tfunc


class Measurement(StructLookUpTableMixin, Named, Typed, Enablable):

    @classmethod
    def update(cls):
        # TODO remove measurements not in DataStruct
        count = 0
        for field in DataStruct.measurement_fields:
            measurement, created = Measurement.objects.get_or_create(
                name=field.metadata.get('path'),
                type=Measurement.Type.from_type(field.type),
            )

            if created:
                measurement.enabled = False
                measurement.save()
                count += 1

        return count

    class Meta:
        verbose_name = _("Measurement")
        verbose_name_plural = _("Measurements")
        # TODO unique constraint
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['name'],
        #         name='%(app_label)s_%(class)s_name_is_unique'
        #     )
        # ]


    def __str__(self):
        return str(_(self.description))


class MeasurementData(Timestamped):
    cold_room = models.ForeignKey(
        ColdRoom,
        db_index=False,
        on_delete=models.DO_NOTHING,
        verbose_name=_('cold room'),
        help_text=_('cold room help text'))
        # related_name=_('measurements_data')

    measurement = models.ForeignKey(
        Measurement,
        db_index=False,
        on_delete=models.DO_NOTHING,
        verbose_name=_('measurement'),
        help_text=_('measurement help text'))
        # related_name=_('measurements_data')

    class Meta:
        abstract = True
        get_latest_by = 'ts'
        indexes = [
            models.Index(
                fields=['cold_room', 'measurement', '-ts'],
                name="%(app_label)s_%(class)s_cidx"
            ),
        ]
        # https://docs.djangoproject.com/en/3.1/ref/models/fields/#foreignkey
        # A database index is automatically created on the ForeignKey. You can disable
        # this by setting db_index to False. You may want to avoid the overhead of an index
        # if you are creating a foreign key for consistency rather than joins, or if you will
        # be creating an alternative index like a partial or multiple column index.

    def __repr__(self):
        return f"{self.ts} {self.measurement.name}"


class BooleanData(SaveOnValueChangeMixin, MeasurementData):
    value = models.BooleanField(
        default=False,
        verbose_name=_('value'),
        help_text=_('measured value description'))

    def __repr__(self):
        return f"{super().__repr__()} {self.value}"

    def get_cache_key(self):
        return (self.__class__, self.cold_room.pk, self.measurement.pk)

    def get_latest_value(self):
        try:
            latest = BooleanData.objects.filter(
                cold_room__pk=self.cold_room.pk,
                measurement__pk=self.measurement.pk
            ).latest('ts')
            return latest.value
        except (exceptions.ObjectDoesNotExist, self.DoesNotExist):
            return None


class IntegerData(MeasurementData):
    value = models.IntegerField(
        default=0,
        verbose_name=_('value'),
        help_text=_('measured value description'))

    def __repr__(self):
        return f"{super().__repr__()} {self.value}"


class FloatData(MeasurementData):
    value = models.FloatField(
        default=0.0,
        verbose_name=_('value'),
        help_text=_('measured value description'))

    def __repr__(self):
        return f"{super().__repr__()} {self.value:.2f}"


class MeasurementDataDownsampled(MeasurementData):
    avg = models.FloatField(
        default=0,
        verbose_name=_('value'),
        help_text=_('average value description'))

    min = models.FloatField(
        default=0,
        verbose_name=_('min'),
        help_text=_('min value description'))

    max = models.FloatField(
        default=0,
        verbose_name=_('max'),
        help_text=_('max value description'))


    objects = tfunc.TableFunctionManager()

    class Form(forms.Form):
        # FIXME order matters
        from_ts        = forms.DateTimeField()
        to_ts          = forms.DateTimeField()
        cold_room_id   = forms.IntegerField()
        measurement_id = forms.IntegerField()
        points         = forms.IntegerField(required=False, initial=500)
        sample_time    = forms.DateTimeField(
            required=False,
            initial=timedelta(seconds=settings.COMMS_TASK_PERIOD)
        )

    @classproperty
    @classmethod
    def function_args(cls):
        return cls.Form.declared_fields

    @classproperty
    @classmethod
    def source_table(cls):
        SUFFIX = "_downsampled"
        if not cls.func_name.endswith(SUFFIX):
            raise NotSupportedError(
                f'By convention the function name {cls.func_name} should be <source_table>{SUFFIX}.'
            )

        return cls.func_name[:-len(SUFFIX)]

    @classproperty
    @classmethod
    def func_name(cls):
        return cls._meta.db_table

    DEFAULT_POINTS = 500   # max points

    @classmethod
    def create_or_replace(cls):
        with connection.cursor() as cursor:
            # FIXME get_bucket_time, downsampled_query executed multiple times
            cursor.execute("""
            create or replace function get_bucket_time (
                ts_from timestamptz,
                ts_to timestamptz,
                points integer default 500,
                sample_time interval default interval '1 sec'
            )
            returns interval as $bucket_time$
                declare bucket_time interval := greatest(
                    (ts_to - ts_from) / (points - 1), sample_time
                );
            begin
                -- Validate args
                if ts_from >= ts_to then
                    raise 'Expected (ts_from: %) < (ts_to: %)', ts_from, ts_to;
                end if;

                if bucket_time < INTERVAL '0 s' then
                    raise 'Expected (bucket_time: %) > 0', bucket_time;
                end if;

                if sample_time < INTERVAL '0 s' then
                    raise 'Expected (sample_time: %) > 0', sample_time;
                end if;

                if bucket_time < sample_time then
                    raise 'Expected (bucket_time: %) > (sample_time: %)', bucket_time, sample_time;
                end if;

                return bucket_time;
            end $bucket_time$ language plpgsql;
            """)

            cursor.execute("""
            create or replace function downsampled_query (
                data_src regclass,
                sample_time interval,
                ts_from timestamptz,
                ts_to timestamptz,
                points integer default 500
            ) returns table (
                ts timestamptz,
                cold_room_id integer,
                measurement_id integer,
                avg float, min float, max float
            ) as $$
                declare bucket_time interval := get_bucket_time(ts_from, ts_to, points, sample_time);
            begin
                return query
                execute format('select
                    time_bucket(%L::interval, d.bucket) as ts,
                    d.cold_room_id, d.measurement_id,
                    avg(d.value)::float, min(d.value_min)::float, max(d.value_max)::float
                    from %s as d
                    where d.bucket between %L::timestamptz and %L::timestamptz
                    group by d.cold_room_id, d.measurement_id, ts
                    order by cold_room_id, measurement_id, ts desc', bucket_time, data_src, ts_from, ts_to);
            end $$ language plpgsql;
            """)

            SQL_CREATE_OR_REPLACE = """
            create or replace function %(func_name)s (
                ts_from %(ts_type)s,
                ts_to %(ts_type)s,
                points integer default %(default_points)s,
                sample_time interval DEFAULT INTERVAL '%(default_sample_time)s sec'
            ) returns table (
                ts %(ts_type)s,
                cold_room_id integer,
                measurement_id integer,
                value float, min float, max float
            ) as $$
                declare bucket_time interval := get_bucket_time(ts_from, ts_to, points, sample_time);

                declare ts_now %(ts_type)s := now();
                declare ts_delta interval  := INTERVAL '0s';

                -- auto-switch ranges
                declare max_ts_delta_1m interval  := '3 days'::interval;        -- 4320 points/metric
                declare max_ts_delta_1h interval  := '180 days'::interval;      -- 4320 points/metric
                declare max_ts_delta_1d interval  := '4320 days'::interval;     -- 4320 points/metric
                declare max_ts_delta_30d interval := '129600 days'::interval;   -- 4320 points/metric (355 years ???)

                declare rp_limit %(ts_type)s      := ts_now - INTERVAL '2 years';
                declare data_src regclass;
            begin
                -- clamp values
                ts_to := LEAST(ts_now, ts_to);
                ts_from := GREATEST(rp_limit, ts_from);
                ts_delta := ts_to - ts_from;

                if ts_delta < max_ts_delta_1m then
                    data_src :=  '%(src_table)s_aggregate_1_minute';
                elsif ts_delta < max_ts_delta_1h then
                    data_src :=  '%(src_table)s_aggregate_1_hour';
                elsif ts_delta < max_ts_delta_1d then
                    data_src := '%(src_table)s_aggregate_1_day';
                elsif ts_delta < max_ts_delta_30d then
                    data_src := '%(src_table)s_aggregate_30_days';
                else
                    raise 'The data range is too large (ts_from: %%, ts_to: %%)', ts_from, ts_to;
                end if;

                return query
                select * from downsampled_query(
                    data_src => data_src,
                    sample_time => sample_time,
                    ts_from => ts_from,
                    ts_to => ts_to,
                    points => points);
            end $$ language plpgsql;
            """ % {
                'func_name': cls.func_name,
                'src_table': cls.source_table,
                'ts_type': 'timestamptz',
                'default_points': cls.DEFAULT_POINTS,
                'default_sample_time': settings.COMMS_TASK_PERIOD, # seconds
            }
            # print(SQL_CREATE_OR_REPLACE)
            cursor.execute(SQL_CREATE_OR_REPLACE)

    @classmethod
    def drop(cls):
        with connection.cursor() as cursor:
            cursor.execute("DROP FUNCTION IF EXISTS get_bucket_time")
            cursor.execute("DROP FUNCTION IF EXISTS downsampled_query")
            cursor.execute("DROP FUNCTION IF EXISTS %(func_name)s" % {
                'func_name': cls.func_name,
            })

    def save(self, *args, **kwargs):
        raise NotSupportedError('This model is tied to a function view, it cannot be saved.')

    class Meta:
        abstract = True

class FloatDataDownsampled(MeasurementDataDownsampled):
    class Meta:
        managed = False
        db_table = 'historical_floatdata_downsampled'
        verbose_name = _('float measurement downsampled')
        verbose_name_plural = _('float measurements downsampled')

class IntegerDataDownsampled(MeasurementDataDownsampled):
    class Meta:
        managed = False
        db_table = 'historical_integerdata_downsampled'
        verbose_name = _('integer measurement downsampled')
        verbose_name_plural = _('integer measurements downsampled')
