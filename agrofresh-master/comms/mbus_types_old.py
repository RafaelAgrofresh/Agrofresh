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

    def _decode(self, decoder: BinaryPayloadDecoder):
        raise NotImplementedError()

    def encode(self):
        encoder = BinaryPayloadBuilder(byteorder=BYTEORDER, wordorder=WORDORDER)
        self._encode(encoder)
        return encoder.to_registers()

    def decode(self, registers):
        decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=BYTEORDER, wordorder=WORDORDER)
        self._decode(decoder)


class MBusBitField(MBusSerializable):
    def _encode(self, encoder: BinaryPayloadBuilder):
        u16value = sum(
            (0x1 << n)
            for n, field in enumerate(fields(self))
            if getattr(self, field.name)
        )
        encoder.add_16bit_uint(u16value)

    def _decode(self, decoder: BinaryPayloadDecoder):
        u16value = decoder.decode_16bit_uint()
        for n, field in enumerate(fields(self)):
            bit = bool(u16value & (0x1 << n))
            setattr(self, field.name, bit)


class MBusStruct(MBusSerializable):
    def _encode(self, encoder: BinaryPayloadBuilder):
        for field in fields(self):
            if field.type is MBusSerializable:
                value = getattr(self, field.name)
                value._encode(encoder)
                continue

            raise Exception(f"Unsupported auto-encoding for {field.name}:{field.type}")

    def _decode(self, decoder: BinaryPayloadDecoder):
        for field in fields(self):
            if field.type is MBusSerializable:
                value = getattr(self, field.name)
                value._decode(decoder)
                continue

            raise Exception(f"Unsupported auto-decoding for {field.name}:{field.type}")


class u16(int):
    @classmethod
    def size(cls):
        return 2

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(self)

    def _decode(self, decoder: BinaryPayloadDecoder):
        return u16(decoder.decode_16bit_uint())


class u32(int):
    @classmethod
    def size(cls):
        return 4

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_32bit_uint(self)

    def _decode(self, decoder: BinaryPayloadDecoder):
        return u32(decoder.decode_32bit_uint())


class i16(int):
    @classmethod
    def size(cls):
        return 2

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_int(self)

    def _decode(self, decoder: BinaryPayloadDecoder):
        return i16(decoder.decode_16bit_int())


class i32(int):
    @classmethod
    def size(cls):
        return 4

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_32bit_int(self)

    def _decode(self, decoder: BinaryPayloadDecoder):
        return i32(decoder.decode_32bit_int())


class f32(float):
    @classmethod
    def size(cls):
        return 4

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_32bit_float(self)

    def _decode(self, decoder: BinaryPayloadDecoder):
        return f32(decoder.decode_32bit_float())

