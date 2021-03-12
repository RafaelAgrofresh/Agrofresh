import csv

from django.db import models as dmodels
from django.db.models.functions import Cast
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from cold_rooms.models import ColdRoom

from . import models


# TODO https://blog.ionelmc.ro/2020/02/02/speeding-up-django-pagination/
# use hypertable_approximate_row_count() ?


# FIXME broken
class TsListFilter(admin.filters.DateFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        if isinstance(field, dmodels.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif isinstance(field, dmodels.DateField):
            today = now.date()
        else:
            raise NotImplementedError()

        any_data, *others = self.links
        self.links = (
            any_data,
            (_('Last 30 seconds'), {
                self.lookup_kwarg_since: str(now),
                self.lookup_kwarg_until: str(now + timezone.timedelta(seconds=30)),
            }),
            (_('Last 5 minutes'), {
                self.lookup_kwarg_since: str(now),
                self.lookup_kwarg_until: str(now + timezone.timedelta(minutes=5)),
            }),
            (_('Last 30 minutes'), {
                self.lookup_kwarg_since: str(now),
                self.lookup_kwarg_until: str(now + timezone.timedelta(minutes=30)),
            }),
            (_('Last 1 hour'), {
                self.lookup_kwarg_since: str(now),
                self.lookup_kwarg_until: str(now + timezone.timedelta(hours=1)),
            }),
            (_('Last 5 hour'), {
                self.lookup_kwarg_since: str(now),
                self.lookup_kwarg_until: str(now + timezone.timedelta(hours=5)),
            }),
            *others,
        )


class TypeListFilter(admin.filters.ChoicesFieldListFilter):
    def choices(self, changelist):
        yield {
            'selected': self.lookup_val is None,
            'query_string': changelist.get_query_string(remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]),
            'display': _('All')
        }
        none_title = ''
        for lookup, title in [
            # (name, name) for name in  models.events.BaseEvent.subclass_choices()
            (models.AlarmEvent.__name__,  models.AlarmEvent.__name__),
            (models.AuthEvent.__name__,  models.AuthEvent.__name__),
            (models.ParameterChangeEvent.__name__,  models.ParameterChangeEvent.__name__)
        ]:
            if lookup is None:
                none_title = title
                continue
            yield {
                'selected': str(lookup) == self.lookup_val,
                'query_string': changelist.get_query_string({self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]),
                'display': title,
            }
        if none_title:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': changelist.get_query_string({self.lookup_kwarg_isnull: 'True'}, [self.lookup_kwarg]),
                'display': none_title,
            }


# https://www.pyscoop.com/django-jsonfield-attributes-in-admin-filter/
class JSONFieldFilter(admin.filters.SimpleListFilter):
    """
    Base JSONFilter class to use by individual attribute filter classes.
    """
    model_json_field_name   = None  # name of the json field column in the model
    json_data_property_name = None  # name of one attribute from json data


    def lookups(self, request, model_admin):
        """
        Returns a list of tuples.
        The 1st element in each tuple is the coded value for the option that
        will appear in the URL query.
        The 2nd element is the human-readable name for the option that will appear
        in the right sidebar.
        """
        if self.model_json_field_name is None:
            raise ImproperlyConfigured(
                f'Filter class {self.__class__.__name__} does not specify "model_json_field_name"'
            )

        if self.json_data_property_name is None:
            raise ImproperlyConfigured(
                f'Filter class {self.__class__.__name__} does not specify "json_data_property_name"'
            )

        field_value_set = set()

        for json_field_data in model_admin.model.objects.values_list(self.model_json_field_name, flat=True):
            field_value_set.add(self.get_child_value_from_json_field_data(json_field_data))

        return [(v, v) for v in field_value_set]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in
        the query string & retrievable via `self.value()`
        """
        if not self.value():
            return queryset

        json_field_query = {
            f'{self.model_json_field_name}__{self.json_data_property_name}': self.value()
        }
        return queryset.filter(**json_field_query)

    def get_child_value_from_json_field_data(self, json_field_data):
        key_list = self.json_data_property_name.split('__')
        for key in key_list:
            if not isinstance(json_field_data, dict) or not key in json_field_data:
                return None
            json_field_data = json_field_data[key]

        return json_field_data


class PrimaryKeyInJSONFieldFilter(JSONFieldFilter):
    NOT_DEFINED = str(None)
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value provided in
        the query string & retrievable via `self.value()`
        """
        value = self.value()
        qpath = f'{self.model_json_field_name}__{self.json_data_property_name}'

        if not value:
            return queryset

        if value == self.NOT_DEFINED:
            return queryset.filter(**{ f'{qpath}__isnull': True })

        return queryset.filter(**{ qpath: int(value) })


class ColdRoomFilter(PrimaryKeyInJSONFieldFilter):
    template = 'admin/dropdown_filter.html'
    model_json_field_name = 'meta'          # Name of the column in the model
    json_data_property_name = 'cold_room'   # property/field name in json data
    title = ColdRoom._meta.verbose_name     # A label for this filter for admin sidebar
    parameter_name = 'cold_room'            # Parameter for the filter that will be used in the URL query

    def lookups(self, request, model_admin):
        lookup = ColdRoom.objects.values_list('id', 'name', 'description')
        lookup = [(pk, f"{name} - {desc}") for (pk, name, desc) in lookup]
        return [(str(None), None), *lookup]


class ParameterFilter(PrimaryKeyInJSONFieldFilter):
    template = 'admin/dropdown_filter.html'
    model_json_field_name = 'meta'          # Name of the column in the model
    json_data_property_name = 'parameter'   # property/field name in json data
    title = models.Parameter._meta.verbose_name # A label for this filter for admin sidebar
    parameter_name = 'parameter'            # Parameter for the filter that will be used in the URL query

    def lookups(self, request, model_admin):
        lookup = [
            (p.pk, f"{p.name} - {p.description}")
            for p in models.Parameter.objects.all()
        ]
        return [(self.NOT_DEFINED, None), *lookup]


class AlarmFilter(PrimaryKeyInJSONFieldFilter):
    template = 'admin/dropdown_filter.html'
    model_json_field_name = 'meta'          # Name of the column in the model
    json_data_property_name = 'alarm'       # property/field name in json data
    title = models.Alarm._meta.verbose_name # A label for this filter for admin sidebar
    parameter_name = 'alarm'                # Parameter for the filter that will be used in the URL query

    def lookups(self, request, model_admin):
        lookup = [
            (a.pk, f"{a.name} - {a.description}")
            for a in models.Alarm.objects.all()
        ]
        return [(self.NOT_DEFINED, None), *lookup]
