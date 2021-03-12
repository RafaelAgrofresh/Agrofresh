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
from .mbus_types_new import (
    i16, i32, u16, u32, f32,
)
from .structs_blocks_new import *
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
        raise NotImplementedError()