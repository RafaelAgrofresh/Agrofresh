from copy import copy
from core.models.mixins import classproperty
from dataclasses import (
    is_dataclass,
    fields,
)
from django.utils.translation import gettext_lazy
from .mbus_types import MemMapped
from . import tags
import math


clamp = lambda value, val_max, val_min: max(val_min, min(val_max, value))
to_bits = lambda data, n: [bool(data & (0x1 << k)) for k in range(n)]
from_bits = lambda bits: sum(0x1 << k for k, bit in enumerate(bits) if bit)

get_tags      = lambda field, default=[tags.IODATA]: field.metadata.get('tags') or default
contains_all  = lambda search: lambda collection: all((item in collection) for item in search)
contains_none = lambda search: lambda collection: not any((item in collection) for item in search)
tagged_as     = lambda *tags: lambda field: contains_all(tags)(get_tags(field))
not_tagged_as = lambda *tags: lambda field: contains_none(tags)(get_tags(field))
merge_tags    = lambda tags1, tags2: list(set(tags1 or []) | set(tags2 or []))

# TODO improve
# * inherited tags are added if fields are retrieved using get_fields()
# * fields should be copied to avoid shared field refereneces in structs (same field & metadata for all instances)
# * preserve tags order

def get_fields(cls_or_instance, recursive=True, prefix=None, tags=None):
    for field in fields(cls_or_instance):
        path = f"{prefix}.{field.name}" if prefix else field.name
        if recursive and is_dataclass(field.type):
            yield from get_fields(
                field.type,
                recursive=recursive,
                prefix=path,
                tags=merge_tags(tags, field.metadata.get('tags')),
            )
        else:
            field = copy(field) # shallow copy
            field.metadata = {
                **field.metadata,
                'path': path,
                'tags': merge_tags(tags, field.metadata.get('tags')),
            }
            yield field


class BaseDataStruct:
    def __getattr__(self, name):
        *subpaths, attr = name.split('.')
        if not subpaths:
            try:
                return super().__getattr__(attr)

            except AttributeError as e:
                raise AttributeError(f"{name} not found in {self.__class__}") from e

        target = self
        for path in subpaths:
            target = getattr(target, path)

        return getattr(target, attr)

    def __setattr__(self, name, value):
        *subpaths, attr = name.split('.')
        if not subpaths:
            return super().__setattr__(attr, value)

        target = self
        for path in subpaths:
            target = getattr(target, path)

        return setattr(target, attr, value)

    @classmethod
    def get_fields(cls):
        raise NotImplementedError()

    @classmethod
    def get_fields_tagged_as(cls, *tags, recursive=True):
        predicate = tagged_as(*tags)
        yield from (
            field
            for field in cls.get_fields()
            if predicate(field)
        )

    @classmethod
    def get_fields_not_tagged_as(cls, *tags, recursive=True):
        predicate = not_tagged_as(*tags)
        yield from (
            field
            for field in cls.get_fields()
            if predicate(field)
        )

    @classmethod
    def get_field(cls, path):
        for field in cls.get_fields():
            if path == field.metadata.get('path'):
                return field

        raise Exception(f"{path} not found")

    @classmethod
    def get_fields_lut(cls):
        def get_address(field):
            if not 'offset' in field.metadata:
                return '--'

            offset = field.metadata.get('offset')
            if not 'bit' in field.metadata:
                return f"HR{offset}"

            bit = field.metadata.get('bit')
            return f"HR{offset}.{bit}"

        return {
            path: {
                'type': field.type.__name__,
                'tags': field.metadata.get('tags') or [tags.IODATA],
                'desc': gettext_lazy(field.metadata.get('description')),
                'addr': get_address(field),
            }
            for field in cls.get_fields()
            if (path := field.metadata.get('path'))
                and not path.startswith("_")
            # isinstance(field, MemMapped)
        }

    def asdict(self):
        def clean_data(x):
            # TODO if isinstance(x, (float, f32)) and not math.isfinite(x):
            if isinstance(x, float) and not math.isfinite(x):
                # prevent JSON serialization errors
                # [NaN, Infinity, -Infinity] are not supported
                return None

            return x

        return {
            path: clean_data(getattr(self, path))
            for field in get_fields(self)
            if (path := field.metadata.get('path'))
                and not path.startswith("_")
        }

    @classmethod
    def get_tags(cls):
        return set(
            tag
            for field in cls.get_fields()
            for tag in get_tags(field)
        )

    @classproperty
    @classmethod
    def alarm_fields(cls):
        return list(cls.get_fields_tagged_as(tags.ALARM))
        # return [
        #     field
        #     for field in cls.get_fields()
        #     if isinstance(field, MemMapped)
        #         and tags.ALARM in get_tags(field)
        #         and not is_dataclass(field.type)
        #         and not field.name.startswith('_')
        # ]

    @classproperty
    @classmethod
    def parameter_fields(cls):
        return list(cls.get_fields_tagged_as(tags.PARAM))
        # return [
        #     field
        #     for field in cls.get_fields()
        #     if isinstance(field, MemMapped)
        #         and tags.PARAM in get_tags(field)
        #         and not is_dataclass(field.type)
        #         and not field.name.startswith('_')
        # ]

    @classproperty
    @classmethod
    def measurement_fields(cls):
        return list(cls.get_fields_tagged_as(tags.IODATA))
        # return [
        #     field
        #     for field in cls.get_fields()
        #     if isinstance(field, MemMapped)
        #         and tags.IODATA in get_tags(field)
        #         and not is_dataclass(field.type)
        #         and not field.name.startswith('_')
        # ]
