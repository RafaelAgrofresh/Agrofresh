from core.models.mixins import LookUpTableMixin
from django.utils.translation import gettext_lazy as _
from comms.structs import DataStruct


class StructLookUpTableMixin(LookUpTableMixin):
    def _get_field_metadata(self):
        try:
            return DataStruct.get_field(self.name).metadata
        except Exception:
            return {}

    def description(self):
        return _(self._get_field_metadata().get('description', ''))
    description.verbose_name=_('description')
    description.help_text=_('description help text')
    description = property(description)

    def tags(self):
        return self._get_field_metadata().get('tags', ['iodata'])
    tags.verbose_name=_('tags')
    tags.help_text=_('tags help text')
    tags = property(tags)

