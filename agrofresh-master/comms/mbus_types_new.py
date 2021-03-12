from dataclasses import fields
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.payload import Endian

BYTEORDER=Endian.Big
WORDORDER=Endian.Big


class MBusSerializable:
    @classmethod
    def size(cls):
        instance = cls()
        return len(instance.encode())

    def _encode(self, encoder: BinaryPayloadBuilder):
        raise NotImplementedError()

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        raise NotImplementedError()

    def encode(self, byteorder=BYTEORDER, wordorder=WORDORDER):
        encoder = BinaryPayloadBuilder(
            byteorder=byteorder,
            wordorder=wordorder,
        )
        self._encode(encoder)
        return encoder.to_registers()

    @classmethod
    def decode(cls, registers, byteorder=BYTEORDER, wordorder=WORDORDER):
        decoder = BinaryPayloadDecoder.fromRegisters(
            registers,
            byteorder=byteorder,
            wordorder=wordorder,
        )
        return cls._decode(decoder)


class MBusBitField(MBusSerializable):
    def _encode(self, encoder: BinaryPayloadBuilder):
        u16value = sum(
            (0x1 << n)
            for n, field in enumerate(fields(self))
            if getattr(self, field.name)
        )
        encoder.add_16bit_uint(u16value)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        u16value = decoder.decode_16bit_uint()
        bitvalues = {
            field.name: bool(u16value & (0x1 << n))
            for n, field in enumerate(fields(cls))
        }
        return cls(**bitvalues)


class MBusStruct(MBusSerializable):
    @staticmethod
    def _validate_field(field):
        if not issubclass(field.type, MBusSerializable):
            raise TypeError(
                f"Unsupported auto-encoding for {field.name}:{field.type}. "
                f"Expected type {MBusSerializable.__name__}:{field.type.__name__}"
            )

    def _encode(self, encoder: BinaryPayloadBuilder):
        for field in fields(self):
            self._validate_field(field)

            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                value = field.type(value)

            value._encode(encoder)

    @classmethod
    def _decode(cls,  decoder: BinaryPayloadDecoder):
        result = {}
        for field in fields(cls):
            cls._validate_field(field)
            result[field.name] = field.type._decode(decoder)

        return cls(**result)


class u8(MBusSerializable, int):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_8bit_uint(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_8bit_uint())


class u16(MBusSerializable, int):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_16bit_uint())


class u32(MBusSerializable, int):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_32bit_uint(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return u32(decoder.decode_32bit_uint())


class u64(MBusSerializable, int):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_64bit_uint(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_64bit_uint())


class i8(MBusSerializable, int):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_8bit_int(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_8bit_int())


class i16(MBusSerializable, int):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_int(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_16bit_int())


class i32(MBusSerializable, int):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_32bit_int(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_32bit_int())


class u64(MBusSerializable, int):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_64bit_int(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_64bit_int())


class f32(MBusSerializable, float):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_32bit_float(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_32bit_float())


class f64(MBusSerializable, float):
    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_64bit_float(self)

    @classmethod
    def _decode(cls, decoder: BinaryPayloadDecoder):
        return cls(decoder.decode_64bit_float())
