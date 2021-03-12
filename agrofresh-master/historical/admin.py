from adminsortable2.admin import CustomInlineFormSet, SortableInlineAdminMixin
from core.admin import (
    ExportCsvMixin,
    ReadOnlyMixin,
    SearchInMemoryMixin,
    SingletonMixin,
)
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models as dmodels
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, path
from django.utils import timezone
from django.utils.html import format_html, format_html_join, mark_safe
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
import historical.admin_filters as filters

from . import models
from cold_rooms.models import ColdRoom


class EnableItemsAdmin(ExportCsvMixin, ReadOnlyMixin, SearchInMemoryMixin, admin.ModelAdmin):
    actions = [
        *ExportCsvMixin.actions,
        'enable',
        'disable',
    ]
    list_display  = ['name', 'description', 'enabled']
    list_filter = ['enabled']
    list_editable = ['enabled']
    search_fields = ['name', 'description'] # description is computed

    def has_change_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        self._notify_model_change(obj)
        super().save_model(request, obj, form, change)

    def enable(self, request, queryset):
        queryset.update(enabled=True)
        for obj in queryset:
            self._notify_model_change(obj)
    enable.short_description = _("enable")

    def disable(self, request, queryset):
        queryset.update(enabled=False)
        for obj in queryset:
            self._notify_model_change(obj)
    disable.short_description = _("disable")

    def _notify_model_change(self, obj):
        from .signals import model_change
        model_change.send(sender=self, model=obj)


@admin.register(models.Measurement)
class MeasurementAdmin(EnableItemsAdmin):
    list_display  = ['name', 'description', 'type', 'enabled']
    list_filter = ['enabled', 'type']
    actions = [
        *EnableItemsAdmin.actions,
        'remove_historical_data',
    ]

    def remove_disabled(self, request, queryset):
        queryset.update(enabled=True)
        for obj in queryset:
            self._notify_model_change(obj)
    remove_disabled.short_description = _("remove historical data")

@admin.register(models.Alarm)
class AlarmAdmin(EnableItemsAdmin): pass


@admin.register(models.Parameter)
class ParameterAdmin(EnableItemsAdmin):
    list_display  = ['name', 'description', 'type', 'enabled']
    list_filter = ['enabled', 'type']


@admin.register(models.Event)
class EventAdmin(ExportCsvMixin, ReadOnlyMixin, admin.ModelAdmin):
    # paginator = DumbPaginator
    list_display = ('ts', 'type', 'description', 'value' )
    list_filter = (
        'ts', # ('ts', filters.TsListFilter),
        ('type', filters.TypeListFilter),
        filters.ColdRoomFilter,
        filters.ParameterFilter,
        filters.AlarmFilter,
    )
    # # https://github.com/hakib/django-admin-lightweight-date-hierarchy
    # date_hierarchy = 'ts'

    list_per_page = 30
    list_max_show_all = 50
    # ordering = ('-ts', 'type', 'data')


# TODO specialized events as proxy model and customized alarm event admin

# https://hakibenita.com/tag/django
"""
date_hierarchy : this index can be used to improve queries generate with date hierarchy
    predicate in PostgresSQL 9.4

CREATE INDEX yourmodel_date_hierarchy_ix ON yourmodel_table (
    extract('day' from created at time zone 'America/New_York'),
    extract('month' from created at time zone 'America/New_York'),
    extract('year' from created at time zone 'America/New_York')
);
"""

"""
Performance considerations with ordering and sorting

To ensure a deterministic ordering of results, the changelist adds
pk to the ordering if it can?t find a single or unique together set
of fields that provide total ordering.

For example, if the default ordering is by a non-unique name field,
then the changelist is sorted by name and pk. This could perform poorly
if you have a lot of rows and don?t have an index on name and pk.
"""


class SortedMeasurementsListForm(forms.ModelForm):
    class Meta:
        model = models.SortedMeasurementsList
        exclude = ('settings',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)

        settings = models.Settings.load()
        selected_qs = settings.default_measurements
        if instance:
            self.fields['measurement'].disabled = True
            selected_qs = selected_qs.exclude(pk__in=[instance.measurement.id])

        self.fields['measurement'].widget.can_change_related = False
        self.fields['measurement'].queryset = (
            # filter enabled measurements and exclude already used
            models.Measurement.objects
                .filter(enabled=True)
                .exclude(id__in=selected_qs.values_list('id', flat=True))
        )


class SortedMeasurementsListFormSet(CustomInlineFormSet):

    def clean(self):
        super().clean()

        # Validate selected measurements uniqueness
        measurement_pks = []
        for form in self.forms:
            if not form.is_valid():
                return # other errors exist, so don't bother
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                measurement = form.cleaned_data['measurement']
                if measurement.pk in measurement_pks:
                    form.add_error('measurement', _(f'Duplicated measurement'))
                    return # raise ValidationError(_(f'Duplicated measurement'))
                measurement_pks.append(measurement.pk)


class SortedMeasurementsListInline(SortableInlineAdminMixin, admin.TabularInline):
    model = models.Settings.default_measurements.through
    formset = SortedMeasurementsListFormSet
    form = SortedMeasurementsListForm
    extra = 1


@admin.register(models.Settings)
class SettingsAdmin(SingletonMixin, admin.ModelAdmin):
    inlines = (SortedMeasurementsListInline,)
