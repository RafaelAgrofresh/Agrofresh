from cold_rooms.models import ColdRoom
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Reset, Button, Layout, HTML
from crispy_forms.bootstrap import FormActions
from historical import models
from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from comms.structs import DataStruct
import custom_widgets as cw


not_null_choices = lambda choices: [(value, label)
    for value, label in choices
    if value]


DATETIME_FMT = '%Y/%m/%d %H:%M:%S'

class BaseFilterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-lg-2"
        self.helper.field_class = "col-lg-8"
        self.helper.form_method = "GET"
        self.helper.add_input(Submit('submitBtn', _('Apply')))
        self.helper.add_input(Reset('resetBtn', _('Reset'),
            css_class='btn-inverse',
            onclick="""
            // this.form.submit()
            window.location.replace(window.location.href.split('?')[0])
            """,
        ))


class HistoricalDataFilterForm(BaseFilterForm):
    ts_range = cw.DateTimeRangeField(
        label=_('Time Range'),
        input_formats=[DATETIME_FMT],
        widget=cw.DateRangeWidget(format=DATETIME_FMT),
        required=False,
    )

    measurements = forms.MultipleChoiceField(
        label=_('measurements'),
        choices=list(
            (m.pk, str(m))
            for m in models.Measurement.objects.filter(enabled=True)
        ),
        widget=cw.FilteredSelectMultipleWidget(
            verbose_name=_('measurements'),
            is_stacked=False,
        ),
        required=False,
    )

    # # TODO custom widget FilteredSelectMultiple
    # class Media:
    #     # Django also includes a few javascript files necessary
    #     # for the operation of this form element. You need to
    #     # include <script src="/admin/jsi18n"></script>
    #     # in the template.
    #     css = {
    #        'all': (
    #            'admin/css/widgets.css',
    #            '/static/css/adminoverrides.css',
    #        )
    #     }
    #     js = (
    #         '/admin/jsi18n/',
    #         #'/static/js/model_multiple_choice_field.js',
    #     )
    # measurements = forms.ModelMultipleChoiceField(
    #     label=_('measurements'),
    #     queryset=models.Measurement.objects.filter(enabled=True),
    #     widget=admin.widgets.FilteredSelectMultiple(
    #         verbose_name=_('measurement'),
    #         is_stacked=False,
    #     )
    # )


class DescribedModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        try:
            return f"{obj.name} - {obj.description}"
        except:
            return "--"


class EventsViewFilterForm(BaseFilterForm):
    ts_range = cw.DateTimeRangeField(
        label=_('Time Range'),
        input_formats=[DATETIME_FMT],
        widget=cw.DateRangeWidget(format=DATETIME_FMT),
        required=False,
    )

    event_type = forms.MultipleChoiceField(
        label=_('Type'),
        widget=forms.CheckboxSelectMultiple,
        choices=[
            (models.AcknowledgeAlarmsEvent.__name__,  models.AcknowledgeAlarmsEvent.__name__),
            (models.AlarmEvent.__name__,  models.AlarmEvent.__name__),
            (models.AuthEvent.__name__,  models.AuthEvent.__name__),
            (models.ParameterChangeEvent.__name__,  models.ParameterChangeEvent.__name__),
            (models.ParameterChangeCommand.__name__,  models.ParameterChangeCommand.__name__),
        ],
        required=False,
    )

    alarm = DescribedModelChoiceField(
        queryset=models.Alarm.objects.all(),
        label=models.Alarm._meta.verbose_name, # _('Alarm'),
        initial=0,
        required=False,
    )

    parameter = DescribedModelChoiceField(
        queryset=models.Parameter.objects.all(),
        label=models.Parameter._meta.verbose_name, # _('Parameter'),
        initial=0,
        required=False,
    )

    tags = forms.MultipleChoiceField(
        choices=[(tag, tag) for tag in DataStruct.get_tags()],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    cold_room = forms.ModelMultipleChoiceField(
        label=ColdRoom._meta.verbose_name,
        widget=forms.CheckboxSelectMultiple,
        queryset=ColdRoom.objects.all(),
        required=False,
    )
