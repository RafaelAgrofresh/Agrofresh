from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from . import models


NAMED_FIELDS = ['name', 'description']


@admin.register(models.ColdRoom)
class ColdRoomAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (*NAMED_FIELDS, 'endpoint',)
    search_fields = (*NAMED_FIELDS,)
