import csv
import sys

from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from functools import update_wrapper
from .models import Sortable


class ExportCsvMixin(admin.ModelAdmin):
    actions = ['export_to_csv']

    def export_to_csv(modeladmin, request, queryset):
        meta = modeladmin.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_to_csv.short_description = _("Export selected to CSV")
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/actions/#setting-permissions-for-actions


class PaginationDisabledMixin(admin.ModelAdmin):
    list_per_page = sys.maxsize


class ReadOnlyMixin(admin.ModelAdmin):
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SearchInMemoryMixin:
    def get_search_results(self, request, queryset, search_term):

        if not self.search_fields or not search_term:
            return super().get_search_results(request, queryset, search_term)

        search_term = search_term.lower()

        def predicate(model):
            return any(
                search_term in str(value).lower()
                for field in self.search_fields
                if (value := getattr(model, field))
            )

        primary_keys = set(
            model.pk
            for model in self.model.objects.all()
            if predicate(model)
        )

        queryset = self.model.objects.filter(id__in=primary_keys)
        use_distinct = False
        return queryset, use_distinct


# # https://hakibenita.medium.com/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41

# class SortableAdminMixin(admin.ModelAdmin):
#     list_display = ('sort_actions',)
#     sortable_by = ('sort_order',)
#     exclude = ('sort_order',)

#     def get_changelist_instance(self, request):
#         # TODO check model is Sortable
#         # TODO find a better place to invoke normalize_sort_order()
#         self.model.objects.normalize_sort_order()
#         return super().get_changelist_instance(request)

#     def get_urls(self):
#         return [
#             *super().get_urls(),
#             path(
#                 '<int:model_id>/moveup',
#                 self.admin_site.admin_view(self.process_sort_moveup),
#                 name='sort-moveup'
#             ),
#             path(
#                 '<int:model_id>/movedown',
#                 self.admin_site.admin_view(self.process_sort_movedown),
#                 name='sort-movedown'
#             ),
#         ]

#     def sort_actions(self, obj):
#         return format_html(
#             '<a class="button" href="{}">Up</a>&nbsp;' # fa fa-sort-up
#             '<a class="button" href="{}">Down</a>',    # fa fa-sort-down
#             reverse('admin:sort-moveup', args=[obj.pk]),
#             reverse('admin:sort-movedown', args=[obj.pk]),
#         )
#     sort_actions.short_description = 'Sort'
#     sort_actions.allow_tags = True

#     def process_sort_moveup(self, request, model_id, *args, **kwargs):
#         sortable = self.get_object(request, model_id)
#         if not isinstance(sortable, Sortable):
#             return self.redirect_to_changelist()

#         index = sortable.sort_order
#         prev_item = self.model.objects.filter(sort_order__lt=index).last()
#         if not isinstance(prev_item, Sortable):
#             return self.redirect_to_changelist()

#         sortable.sort_order = prev_item.sort_order
#         prev_item.sort_order = index

#         sortable.save()
#         prev_item.save()
#         return self.redirect_to_changelist()

#     def process_sort_movedown(self, request, model_id, *args, **kwargs):
#         sortable = self.get_object(request, model_id)
#         if not isinstance(sortable, Sortable):
#             return self.redirect_to_changelist()

#         index = sortable.sort_order
#         next_item = self.model.objects.filter(sort_order__gt=index).first()

#         if not isinstance(next_item, Sortable):
#             return self.redirect_to_changelist()

#         sortable.sort_order = next_item.sort_order
#         next_item.sort_order = index
#         sortable.save()
#         next_item.save()
#         return self.redirect_to_changelist()

#     def redirect_to_changelist(self):
#         # return HttpResponseRedirect(request.path_info)
#         # not working as expected
#         return_url = 'admin:%s_%s_changelist' % (
#             self.model._meta.app_label,
#             self.model._meta.model_name,
#         )
#         url = reverse(return_url)
#         return HttpResponseRedirect(url)


class SingletonMixin(admin.ModelAdmin):
    def get_queryset(self, request):
        self.model.load()
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                kwargs = { 'object_id': "1", **kwargs }
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        return [
            path('', wrap(self.change_view), name='%s_%s_changelist' % info),
            path('add/', wrap(self.add_view), name='%s_%s_add' % info),
            path('autocomplete/', wrap(self.autocomplete_view), name='%s_%s_autocomplete' % info),
            path('<path:object_id>/history/', wrap(self.history_view), name='%s_%s_history' % info),
            path('<path:object_id>/delete/', wrap(self.delete_view), name='%s_%s_delete' % info),
            path('<path:object_id>/change/', wrap(self.change_view), name='%s_%s_change' % info),
            # For backwards compatibility (was the change url before 1.9)
            path('<path:object_id>/', wrap(RedirectView.as_view(
                pattern_name='%s:%s_%s_change' % ((self.admin_site.name,) + info)
            ))),
        ]
