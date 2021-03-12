import json
import re
from collections import OrderedDict
from datetime import date, datetime, timedelta

from dateutil import relativedelta
from django import forms
from django.conf import settings
from django.contrib.admin import widgets as admin_widgets
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import formats, timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


__all__ = ['DatePickerWidget', 'DateRangeWidget', 'DateTimeRangeWidget', 'add_month', 'common_dates']

format_to_js = {
    '%m': 'MM',
    '%d': 'DD',
    '%Y': 'YYYY',
    '%y': 'YY',
    '%B': 'MMMM',
    '%b': 'MMM',
    '%M': 'mm',
    '%H': 'HH',
    '%I': 'hh',
    '%p': 'A',
    '%S': 'ss',
    }

format_to_js_re = re.compile(r'(?<!\w)(' + '|'.join(format_to_js.keys()) + r')\b')


def add_month(start_date, months):
    return start_date + relativedelta.relativedelta(months=months)

def start_of_day(d):
    return datetime.combine(date(d.year, d.month, d.day), datetime.min.time())

def end_of_day(d):
    return datetime.combine(date(d.year, d.month, d.day), datetime.max.time())

# def common_dates(start_date=timezone.now()):
#     return OrderedDict([
#         (_('Last %(n)s hours')  % { 'n': 6 },   (start_date - timedelta(hours=6),   start_date)),
#         (_('Last %(n)s hours')  % { 'n': 12 },  (start_date - timedelta(hours=12),  start_date)),
#         (_('Last %(n)s hours')  % { 'n': 24 },  (start_date - timedelta(hours=24),  start_date)),
#         (_('Last %(n)s days')   % { 'n': 7 },   (start_date - timedelta(days=7),    start_date)),
#         (_('Last %(n)s days')   % { 'n': 15 },  (start_date - timedelta(days=15),   start_date)),
#         (_('Last %(n)s days')   % { 'n': 30 },  (start_date - timedelta(days=30),   start_date)),
#         (_('Last %(n)s days')   % { 'n': 90 },  (start_date - timedelta(days=90),   start_date)),
#         (_('Last %(n)s days')   % { 'n': 180 }, (start_date - timedelta(days=180),  start_date)),
#     ])

# def common_dates(start_date=date.today()):
#     one_day = timedelta(days=1)
#     return OrderedDict([
#         (_('Today'), (
#             start_of_day(start_date),
#             end_of_day(start_date),
#         )),
#         (_('Yesterday'), (
#             start_of_day(start_date - one_day),
#             end_of_day(start_date - one_day),
#         )),
#         (_('This week'), (
#             start_of_day(start_date - timedelta(days=start_date.weekday())),
#             end_of_day(start_date),
#         )),
#         (_('Last week'), (
#             start_of_day(start_date - timedelta(days=start_date.weekday() + 7)),
#             end_of_day(start_date - timedelta(days=start_date.weekday() + 1)),
#         )),
#         (_('Week ago'), (
#             start_of_day(start_date - timedelta(days=7)),
#             end_of_day(start_date),
#         )),
#         (_('This month'), (
#             start_of_day(start_date.replace(day=1)),
#             end_of_day(start_date),
#         )),
#         (_('Last month'), (
#             start_of_day(add_month(start_date.replace(day=1), -1)),
#             end_of_day(start_date.replace(day=1) - one_day),
#         )),
#         (_('3 months'), (
#             start_of_day(add_month(start_date, -3)),
#             end_of_day(start_date),
#         )),
#         (_('Year'), (
#             start_of_day(add_month(start_date, -12)),
#             end_of_day(start_date),
#         )),
#     ])


class DateRangeWidget(forms.TextInput):
    format_key = 'DATE_INPUT_FORMATS'
    template_name = 'daterangewidget.html'

    def __init__(self, picker_options=None, attrs=None, format=None, separator=' - ', clearable=False):
        super(DateRangeWidget, self).__init__(attrs)
        self.separator = separator
        # breakpoint()
        # if format and format.endswith():
        #     self.format = format
        self.format = format
        picker_options_defaults = {
            # defaults (http://www.daterangepicker.com/)
            'showDropdowns': True,
            'timePicker': True,
            'timePicker24Hour': True,
            # 'ranges': common_dates, computed in JS
        }

        self.picker_options = { **picker_options_defaults, **picker_options } \
            if picker_options else picker_options_defaults

        self.clearable_override = clearable

        if 'class' not in self.attrs:
            self.attrs['class'] = 'form-control'

    def clearable(self):
        """clearable if the field is an optional field or if explicitly set as clearable"""
        # Can't be set on init as is_required is set *after* widget initialisation
        # https://github.com/django/django/blob/d5f4ce9849b062cc788988f2600359dc3c2890cb/django/forms/fields.py#L100
        return not self.is_required or self.clearable_override

    def _get_format(self):
        return self.format or formats.get_format(self.format_key)[0]

    def _format_date_value(self, value):
        return formats.localize_input(value, self._get_format())

    def format_value(self, value):
        if isinstance(value, tuple):
            return self._format_date_value(value[0]) + \
                   self.separator + \
                   self._format_date_value(value[1])
        else:
            return value

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        date_format = format_to_js_re.sub(lambda m: format_to_js[m.group()], self._get_format())

        default_picker_options = {
            "locale": {
                "format": date_format,
                "applyLabel": _("Apply"),
                "cancelLabel": _("Clear"),
                "fromLabel": _("From"),
                "toLabel": _("To"),
                "customRangeLabel": _("Custom Range"),
                "daysOfWeek": [
                    _("Su"),
                    _("Mo"),
                    _("Tu"),
                    _("We"),
                    _("Th"),
                    _("Fr"),
                    _("Sa"),
                ],
                "monthNames": [
                    _("January"),
                    _("February"),
                    _("March"),
                    _("April"),
                    _("May"),
                    _("June"),
                    _("July"),
                    _("August"),
                    _("September"),
                    _("October"),
                    _("November"),
                    _("December"),
                ],
                "firstDay": 1
            }
        }

        if self.clearable():
            default_picker_options['autoUpdateInput'] = False
            # default_picker_options['locale']['cancelLabel'] = _("Clear")

        # Rename for clarity
        picker_options = default_picker_options
        picker_options.update(self.picker_options)

        # Computed in JS
        # # If range is a dict of functions, call with 'today' as argument
        # if 'ranges' in picker_options:
        #     # ranges = OrderedDict(picker_options['ranges'])
        #     ranges = OrderedDict(
        #         # invoke if callable
        #         picker_options['ranges']()
        #         if callable(picker_options['ranges'])
        #         else picker_options['ranges']
        #     )

        #     for k, v in ranges.items():
        #         if callable(v):
        #             ranges[k] = v(timezone.now())
        #     picker_options['ranges'] = ranges

        # Update context for template
        picker_options_json = json.dumps(picker_options, cls=DjangoJSONEncoder)
        context['widget']['picker'] = {
            'options': {
                'json': mark_safe(picker_options_json),
                'python': picker_options,
            },
            'clearable': self.clearable(),
            'separator': self.separator,
        }

        return context


class DateTimeRangeWidget(DateRangeWidget):
    format_key = 'DATETIME_INPUT_FORMATS'

    def __init__(self, *args, **kwargs):
        super(DateTimeRangeWidget, self).__init__(*args, **kwargs)

        if 'timePicker' not in self.picker_options:
            self.picker_options['timePicker'] = True


class DatePickerWidget(DateRangeWidget):
    def __init__(self, *args, **kwargs):
        super(DatePickerWidget, self).__init__(*args, **kwargs)

        if 'singleDatePicker' not in self.picker_options:
            self.picker_options['singleDatePicker'] = True


class FilteredSelectMultipleWidget(forms.SelectMultiple):
    """
    A SelectMultiple with a JavaScript filter interface.

    Note that the resulting JavaScript assumes that the jsi18n
    catalog has been loaded in the page
    """
    # Customization of admin.widgets.FilteredSelectMultiple
    # template_name = 'filteredselectmultiplewidget.html'
    # option_template_name = 'measurementoption.html'

    class Media:
        css = {
            'all': (
                'admin/css/widgets.css',
                'admin/css/overrides.css',
            )
        }
        js = [
            'admin/js/core.js',
            'admin/js/SelectBox.js',
            'admin/js/SelectFilter2.js',
            '/admin/jsi18n/',
        ]

    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        self.verbose_name = verbose_name
        self.is_stacked = is_stacked
        super().__init__(attrs, choices)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['class'] = 'selectfilter'
        if self.is_stacked:
            context['widget']['attrs']['class'] += 'stacked'
        context['widget']['attrs']['data-field-name'] = self.verbose_name
        context['widget']['attrs']['data-is-stacked'] = int(self.is_stacked)
        return context


class SortOrderInput(admin_widgets.AdminBigIntegerFieldWidget):
    HTML_INPUT_CLASS = 'sort-order-input'

    def render(self, name, value, attrs=None, renderer=None):
        if 'class' in attrs:
            attrs['class'] = attrs['class'] + ' ' + self.HTML_INPUT_CLASS
        else:
            attrs['class'] = self.HTML_INPUT_CLASS

        attrs['data-label-up'] = _("Up")
        attrs['data-label-down'] = _("Down")

        return super().render(name, value, attrs, renderer=renderer)

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        js = [
            'admin/js/vendor/jquery/jquery{0}.js'.format(extra),
            'admin/js/jquery.init.js',
            'admin/js/core.js',
            'js/sort_order_input.js',
        ]

        css = {
            'screen': (
                'css/sort_order_input.css',
            )
        }
        return forms.Media(css=css, js=js)
