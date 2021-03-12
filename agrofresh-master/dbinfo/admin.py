import functools
from core.admin import PaginationDisabledMixin, ReadOnlyMixin
from django.contrib import admin
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.TableInfo)
class TableInfoAdmin(PaginationDisabledMixin, ReadOnlyMixin, admin.ModelAdmin):
    change_list_template = 'admin/table_info_change_list.html'
    list_display = (
        'table_name',
        'is_hypertable',
        'formatted_table_size',
        'formatted_index_size',
        'formatted_total_size',
    )
    list_filter = ('is_hypertable',)
    search_fields = ('table_name',)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        response.context_data['summary'] = qs.summary()
        return response

    def formatted_table_size(self, obj):
        return filesizeformat(obj.table_size)
    formatted_table_size.admin_order_field = 'table_size'
    formatted_table_size.short_description = _('table size')

    def formatted_index_size(self, obj):
        return filesizeformat(obj.index_size)
    formatted_index_size.admin_order_field = 'index_size'
    formatted_index_size.short_description = _('index size')

    def formatted_total_size(self, obj):
        return filesizeformat(obj.total_size)
    formatted_total_size.admin_order_field = 'total_size'
    formatted_total_size.short_description = _('total size')
