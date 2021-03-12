from dataclasses import (
    dataclass,
    fields,
    Field,
    MISSING,
)

class MemMapped(Field):
    @staticmethod
    def new(*, default=MISSING, default_factory=MISSING, init=True, repr=True,
            hash=None, compare=True, metadata=None):

        if default is not MISSING and default_factory is not MISSING:
            raise ValueError('cannot specify both default and default_factory')

        return MemMapped(default, default_factory, init, repr, hash, compare, metadata)


class EEPROM(MemMapped):
    @staticmethod
    def new(*, default=MISSING, default_factory=MISSING, init=True, repr=True,
            hash=None, compare=True, metadata=None):

        if default is not MISSING and default_factory is not MISSING:
            raise ValueError('cannot specify both default and default_factory')

        return EEPROM(default, default_factory, init, repr, hash, compare, metadata)


from .mbus_types_old import *
# from .mbus_types_new import *

