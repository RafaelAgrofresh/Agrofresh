from core.models.mixins import classproperty
from dataclasses import (
    dataclass,
    field,
    is_dataclass,
)
from django.utils.translation import gettext_lazy, gettext_noop as _
from pymodbus.payload import (
    BinaryPayloadBuilder,
    BinaryPayloadDecoder,
)
from .mbus_types import (
    MemMapped,
    EEPROM,
)
from .mbus_types_old import (
    i16, i32, u16, u32, f32,
)
from .structs_blocks_old import *
from .structs_common import (
    BaseDataStruct,
    get_fields,
    get_tags,
    tagged_as,
    not_tagged_as,
)
from .tags import *


@dataclass
class DataStruct(
    BaseDataStruct,
    Block30,
    Block29, Block28, Block27, Block26, Block25,
    Block24, Block23, Block22, Block21, Block20,
    Block19, Block18, Block17, Block16, Block15,
    Block14, Block13, Block12, Block11, Block10,
    Block09, Block08, Block07, Block06, Block05,
    Block04, Block03, Block02, Block01, Block00,
):
    _prev = {}

    humidity    : f32  = field(default=0.0,   metadata={'description': _('Humedad'),        'tags': [COMPUTED]})
    temperature : f32  = field(default=0.0,   metadata={'description': _('Temperatura'),    'tags': [COMPUTED]})
    CO2         : f32  = field(default=0.0,   metadata={'description': _('CO2'),            'tags': [COMPUTED]})
    C2H4        : f32  = field(default=0.0,   metadata={'description': _('C2H4'),           'tags': [COMPUTED]})
    systemOn    : bool = field(default=False, metadata={'description': _('Marcha'),         'tags': [COMPUTED]})
    systemOff   : bool = field(default=True,  metadata={'description': _('Paro'),           'tags': [COMPUTED]})
    openDoor    : bool = field(default=False, metadata={'description': _('Puarta abierta'), 'tags': [COMPUTED]})
    anyAlarm    : bool = field(default=False, metadata={'description': _('Alarmas activas'), 'tags': [COMPUTED]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        for cls in reversed(DataStruct.__mro__):
            if cls.__name__.startswith('Block'):
                try:
                    cls._encode(self, encoder)
                except Exception as e:
                    raise Exception(f"Error encoding {cls}") from e

    def _decode(self, decoder: BinaryPayloadDecoder):
        self._prev = self.asdict()

        for cls in reversed(DataStruct.__mro__):
            if cls.__name__.startswith('Block'):
                try:
                    cls._decode(self, decoder)
                except Exception as e:
                    raise Exception(f"Error decoding {cls}") from e

        self._update_computed_values()

    def _update_computed_values(self):
        self.humidity    = self.humidityInside
        self.temperature = self.temperatureInside
        self.CO2         = self.CO2Measure
        self.C2H4        = self.C2H4Measure
        self.systemOn    = self.onOffSystem
        self.systemOff   = not self.onOffSystem
        self.openDoor    = self.photocell1 or self.photocell2
        self.anyAlarm    = any(
            getattr(self, field.metadata.get('path'))
            for field in self.alarm_fields
        )

    @property
    def onchange(self):
        return OnChangeProxy(self)

    @property
    def posedge(self):
        return PosEdgeProxy(self)

    @classmethod
    def get_fields(cls):
        offset, bits = 0, 0

        for field in get_fields(cls):
            base = offset

            if field.type == bool:
                field.metadata = {
                    **field.metadata,
                    'offset': base,
                    'bit': bits,
                    'size': 1,
                }
                yield field

                bits += 1
                if bits % 16 == 0:
                    offset, bits = (offset + 1, 0)
                continue

            if bits > 0:
                offset, bits = (offset + 1, 0)
                base = offset

            if field.type in (u16, i16, u32, i32, f32):
                mb_registers = int(field.type.size() / 2) # 16bit registers
                offset, bits = (offset + mb_registers, 0)

            else:
                yield field
                continue
                # return Exception(f"Unknown size of {field.type} @ {field.metadata.get('path')}")

            field.metadata = {
                **field.metadata,
                'offset': base,
                'size': offset - base,
            }
            yield field

    def randomize(self):
        for field in self.get_fields():
            path  = field.metadata.get('path')

            if not isinstance(field, MemMapped):
                continue

            if field.type == bool:
                value = getattr(self, path, False)
                rand_value = randrange(0, 10)
                value = bool(
                    (not value and rand_value > 8) or
                    (value and rand_value > 2))
                setattr(self, path, value)
                continue

            # value_range = range_LUT.get(field.name, [0, 100])
            value_range = [0, 100]
            if field.type in (int, i16, i32, u16, u32):
                value = getattr(self, path, 0)
                value = randrange(value_range[0], value_range[1])
                setattr(self, path, value)
                continue

            if field.type in (float, f32):
                value = getattr(self, path, 0.0)
                if value == 0.0: value = (value_range[1] - value_range[0]) / 2
                value += (value_range[1] - value_range[0]) * uniform(-0.05, 0.05)
                value = clamp(value, value_range[1], value_range[0])
                setattr(self, path, value)
                continue

            print(f'Unhandled {field.type}')


class OnChangeProxy(object):
    def __init__(self, target):
        self.target = target

    def __getattr__(self, attr):
        prev_val = self.target._prev.get(attr)
        next_val = getattr(self.target, attr)
        return prev_val != next_val

class PosEdgeProxy(OnChangeProxy):
    def __init__(self, target):
        self.target = target

    def __getattr__(self, attr):
        changed = super().__getattr__(attr)
        if not changed:
            return False

        next_val = getattr(self.target, attr)
        if not isinstance(next_val, bool):
            return False

        return next_val