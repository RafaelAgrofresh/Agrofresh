from collections import Counter
from dataclasses import (
    dataclass, field, fields, is_dataclass
)
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from .structs_common import (
    get_tags,
    contains_all,
    contains_none,
    tagged_as,
    not_tagged_as,
)
from . import structs_old as old
from . import structs_new as new
from .mbus_types_new import (
    MBusBitField,
    MBusStruct,
    u8, u16, u32,
    i8, i16, i32,
    f32, f64,
)
import json


class DummyField:
    def __init__(self, **metadata):
        self.metadata = metadata

class TagsTestCase(TestCase):
    def test_contains_all(self):
        collection = ['tag1', 'tag2', 'tag3']
        self.assertTrue(contains_all(['tag1', 'tag2'])(collection))
        self.assertFalse(contains_all(['tag1', 'nop'])(collection))

    def test_contains_none(self):
        collection = ['tag1', 'tag2', 'tag3']
        self.assertTrue(contains_none(['nop1', 'nop2'])(collection))
        self.assertFalse(contains_none(['tag1', 'nop'])(collection))

    def test_get_tags(self):
        TAGS = ['tag1', 'tag2', 'tag3']
        field = DummyField(tags=TAGS)
        tags  = get_tags(field)
        self.assertEquals(TAGS, tags)

    def test_tagged_as(self):
        TAGS = ['tag1', 'tag2', 'tag3']
        field = DummyField(tags=TAGS)
        predicate1 = tagged_as(*TAGS)
        predicate2 = tagged_as(*TAGS[:-1])
        predicate3 = tagged_as(*[f'nop{tag}' for tag in TAGS])
        self.assertTrue(predicate1(field))
        self.assertTrue(predicate2(field))
        self.assertFalse(predicate3(field))

    def test_not_tagged_as(self):
        TAGS = ['tag1', 'tag2', 'tag3']
        field = DummyField(tags=TAGS)
        predicate1 = not_tagged_as(*TAGS)
        predicate2 = not_tagged_as(*TAGS[:-1])
        predicate3 = not_tagged_as(*[f'nop{tag}' for tag in TAGS])
        self.assertFalse(predicate1(field))
        self.assertFalse(predicate2(field))
        self.assertTrue(predicate3(field))


class MBusTypesTestCase(TestCase):
    TYPE_ENC_DEC_CASES = [
        (u8, 1), (u16, 1), (u32, 1),
        (i8, 1), (i16, 1), (i32, 1),
        (f32, 1.2345),
        (f64, 1.2345),
    ]

    def test_type_encode_decode(self):
        def test_func(cls, value):
            cvalue  = cls(value) if not isinstance(value, cls) else value
            encoded = cvalue.encode()
            decoded = cls.decode(encoded)
            self.assertTrue(isinstance(cvalue, cls))
            self.assertTrue(isinstance(encoded, list))
            self.assertTrue(isinstance(decoded, cls))
            self.assertEqual(cvalue, value)

        for  cls, value in self.TYPE_ENC_DEC_CASES:
            test_func(cls, value)

    def test_bitfield(self):
        @dataclass
        class SampleFlags(MBusBitField):
            bit_00 : bool = field(default=False)
            bit_01 : bool = field(default=False)
            bit_02 : bool = field(default=False)
            bit_03 : bool = field(default=False)
            bit_04 : bool = field(default=False)
            bit_05 : bool = field(default=False)
            bit_06 : bool = field(default=False)
            bit_07 : bool = field(default=False)
            bit_08 : bool = field(default=False)
            bit_09 : bool = field(default=False)
            bit_10 : bool = field(default=False)
            bit_11 : bool = field(default=False)
            bit_12 : bool = field(default=False)
            bit_13 : bool = field(default=False)
            bit_14 : bool = field(default=False)
            bit_15 : bool = field(default=False)

        def test_func(flags, enc_expected):
            encoded = flags.encode()
            decoded = SampleFlags.decode(encoded)
            self.assertTrue(isinstance(encoded, list))
            self.assertTrue(isinstance(decoded, SampleFlags))
            self.assertEquals(enc_expected, encoded)
            self.assertEquals(flags, decoded)

        flags = SampleFlags()
        test_func(flags, [0])

        flags.bit_00 = True
        test_func(flags, [1])

        flags.bit_00 = False
        flags.bit_01 = True
        test_func(flags, [2])

        flags.bit_01 = False
        flags.bit_15 = True
        test_func(flags, [1<<15])

    def test_struct(self):
        @dataclass
        class Struct1(MBusStruct):
            field_00 : u16 = field(default=False)
            field_01 : u32 = field(default=False)
            field_02 : u16 = field(default=False)

        expected = [1, 2, 3, 4]
        struct = Struct1(field_00=1, field_01=(2 << 16) | 3, field_02=4)
        encoded = struct.encode()
        decoded = Struct1.decode(encoded)
        self.assertTrue(isinstance(encoded, list))
        self.assertTrue(isinstance(decoded, Struct1))
        self.assertEquals(expected, encoded)
        self.assertEquals(struct, decoded)

    def test_nested_struct(self):
        @dataclass
        class Struct1(MBusStruct):
            field_00 : u16 = field(default=False)
            field_01 : u32 = field(default=False)
            field_02 : u16 = field(default=False)

        @dataclass
        class Struct2(MBusStruct):
            field_00 : u16 = field(default=False)
            field_01 : Struct1 = field(default_factory=Struct1)
            field_02 : Struct1 = field(default_factory=Struct1)

        expected = [
            1,
            2, 3, 4, 5,
            6, 7, 8, 9,
        ]
        struct = Struct2(
            field_00=1,
            field_01=Struct1(field_00=2, field_01=(3 << 16) | 4, field_02=5),
            field_02=Struct1(field_00=6, field_01=(7 << 16) | 8, field_02=9),
        )
        encoded = struct.encode()
        decoded = Struct2.decode(encoded)
        self.assertTrue(isinstance(encoded, list))
        self.assertTrue(isinstance(decoded, Struct2))
        self.assertEquals(expected, encoded)
        self.assertEquals(struct, decoded)


class OldDataStructTestCase(TestCase):
    def test_nested_properties_get(self):
        d = old.DataStruct()
        self.assertTrue(hasattr(d, "pidHumidity.pCoefficient"))
        self.assertEquals(getattr(d, "pidHumidity.pCoefficient"), 0)
        self.assertFalse(hasattr(d, "non_existing_property"))
        self.assertRaises(AttributeError, lambda: getattr(d, "non_existing_property"))

    def test_nested_properties_set(self):
        d = old.DataStruct()
        setattr(d, "pidHumidity.pCoefficient", 10)
        self.assertEquals(getattr(d, "pidHumidity.pCoefficient"), 10)
        self.assertEquals(getattr(d, "pidHumidity.pCoefficient"), d.pidHumidity.pCoefficient)
        self.assertRaises(AttributeError, lambda: setattr(d, "non.existing.property", 1))

    def test_unique_names(self):
        fields = old.DataStruct.get_fields()
        paths  = [field.metadata.get('path') for field in fields]
        self.assert_unique_elements(paths)

    def test_recursive_fields_lookup(self):
        fields1 = list(fields(old.DataStruct))
        fields2 = list(old.DataStruct.get_fields()) # default recursive=True
        self.assertGreater(len(fields2), len(fields1))

    def test_field_tags_based_filtering(self):
        fieldset = list(old.DataStruct.get_fields())
        filtered = list(old.DataStruct.get_fields_tagged_as('param'))
        self.assertGreater(len(filtered), 0)
        self.assertGreater(len(fieldset), len(filtered))

    def test_asdict_not_finite_float_encoding(self):
        d = old.DataStruct()
        d.pidC2H4.pCoefficient = float('nan')
        d.pidC2H4.iCoefficient = float('inf')
        d.pidC2H4.dCoefficient = -float('inf')
        payload = d.asdict()
        encoded = json.dumps(payload, cls=DjangoJSONEncoder, allow_nan=False)
        decoded = json.loads(encoded)
        self.assertEquals(payload, decoded)

    def test_field_tagged_as_predicate(self):
        field1 = field(default=0, metadata={'tags': ['tag1', 'tag2']})
        self.assertTrue(tagged_as('tag1', 'tag2')(field1))
        self.assertFalse(tagged_as('tag3', 'tag4')(field1))

    def test_field_not_tagged_as_predicate(self):
        field1 = field(default=0, metadata={'tags': ['tag1', 'tag2']})
        self.assertFalse(not_tagged_as('tag1')(field1))
        self.assertFalse(not_tagged_as('tag2')(field1))
        self.assertTrue(not_tagged_as('tag3')(field1))
        self.assertTrue(not_tagged_as('tag3', 'tag4')(field1))

    def test_tagged_fields_helpers(self):
        alarms = old.DataStruct.alarm_fields
        params = old.DataStruct.parameter_fields
        measurements = old.DataStruct.measurement_fields
        self.assertTrue(len(alarms) > 0)
        self.assertTrue(len(params) > 0)
        self.assertTrue(len(measurements) > 0)

        get_paths = lambda fields: [f.metadata.get('path') for f in fields]
        self.assert_unique_elements(get_paths(alarms))
        self.assert_unique_elements(get_paths(params))
        self.assert_unique_elements(get_paths(measurements))

    def assert_unique_elements(self, elements):
        # return len(set(elements)) == len(elements)
        for element, cnt in Counter(elements).items():
            self.assertEquals(cnt, 1, f"duplicated element {element}")


class NewDataStructTestCase(TestCase):
    def test_nested_properties_get(self):
        d = new.DataStruct()
        self.assertTrue(hasattr(d, "pidHumidity.pCoefficient"))
        self.assertEquals(getattr(d, "pidHumidity.pCoefficient"), 0)
        self.assertFalse(hasattr(d, "non_existing_property"))
        self.assertRaises(AttributeError, lambda: getattr(d, "non_existing_property"))

    def test_nested_properties_set(self):
        d = new.DataStruct()
        setattr(d, "pidHumidity.pCoefficient", 10)
        self.assertEquals(getattr(d, "pidHumidity.pCoefficient"), 10)
        self.assertEquals(getattr(d, "pidHumidity.pCoefficient"), d.pidHumidity.pCoefficient)
        self.assertRaises(AttributeError, lambda: setattr(d, "non.existing.property", 1))

    def test_unique_names(self):
        fields = new.DataStruct.get_fields()
        paths  = [field.metadata.get('path') for field in fields]
        self.assert_unique_elements(paths)

    def test_recursive_fields_lookup(self):
        fields1 = list(fields(new.DataStruct))
        fields2 = list(new.DataStruct.get_fields()) # default recursive=True
        self.assertGreater(len(fields2), len(fields1))

    def test_field_tags_based_filtering(self):
        fieldset = list(new.DataStruct.get_fields())
        filtered = list(new.DataStruct.get_fields_tagged_as('param'))
        self.assertGreater(len(filtered), 0)
        self.assertGreater(len(fieldset), len(filtered))

    def test_asdict_not_finite_float_encoding(self):
        d = new.DataStruct()
        d.pidC2H4.pCoefficient = float('nan')
        d.pidC2H4.iCoefficient = float('inf')
        d.pidC2H4.dCoefficient = -float('inf')
        payload = d.asdict()
        encoded = json.dumps(payload, cls=DjangoJSONEncoder, allow_nan=False)
        decoded = json.loads(encoded)
        self.assertEquals(payload, decoded)

    def test_field_tagged_as_predicate(self):
        field1 = field(default=0, metadata={'tags': ['tag1', 'tag2']})
        self.assertTrue(tagged_as('tag1', 'tag2')(field1))
        self.assertFalse(tagged_as('tag3', 'tag4')(field1))

    def test_field_not_tagged_as_predicate(self):
        field1 = field(default=0, metadata={'tags': ['tag1', 'tag2']})
        self.assertFalse(not_tagged_as('tag1')(field1))
        self.assertFalse(not_tagged_as('tag2')(field1))
        self.assertTrue(not_tagged_as('tag3')(field1))
        self.assertTrue(not_tagged_as('tag3', 'tag4')(field1))

    def test_tagged_fields_helpers(self):
        alarms = new.DataStruct.alarm_fields
        params = new.DataStruct.parameter_fields
        measurements = new.DataStruct.measurement_fields
        self.assertTrue(len(alarms) > 0)
        self.assertTrue(len(params) > 0)
        self.assertTrue(len(measurements) > 0)

        get_paths = lambda fields: [f.metadata.get('path') for f in fields]
        self.assert_unique_elements(get_paths(alarms))
        self.assert_unique_elements(get_paths(params))
        self.assert_unique_elements(get_paths(measurements))

    def assert_unique_elements(self, elements):
        # return len(set(elements)) == len(elements)
        for element, cnt in Counter(elements).items():
            self.assertEquals(cnt, 1, f"duplicated element {element}")


class OldDataStructAndNewDataStructCompatibilityTestCase(TestCase):
    def test_fields_campatibility(self):
        d_old = old.DataStruct()
        d_new = new.DataStruct()
        fieldset_old = d_old.get_fields()
        fieldset_new = d_new.get_fields()

        for a, b in zip(fieldset_old, fieldset_new):
            self.assertEquals(a.name, b.name, f"{a.name} != {b.name}")

            self.assertEquals(a.type.__name__, b.type.__name__,
                f"{a.name} -> {a.type.__name__} != {b.type.__name__}")

            self.assertEquals(a.default, b.default,
                f"{a.name} -> {a.default} != {b.default}")

            self.assertEquals(a.metadata, b.metadata,
                f"{a.name} -> {a.metadata} != {b.metadata}")

            value_old = getattr(d_old, a.metadata.get('path'))
            value_new = getattr(d_new, b.metadata.get('path'))
            self.assertEquals(value_old, value_new, f"{a.name} -> {value_old} != {value_new}")

    def test_encoding_camptibility(self):
        data = old.DataStruct()
        value_func = {
            'i16': lambda n: int(n) % 100,
            'i32': lambda n: int(n),
            'u16': lambda n: int(n) % 100,
            'u32': lambda n: int(n),
            'f32': lambda n: float(n),
            'bool': lambda n: bool(n % 2 == 0),
            'str': lambda n: str(n),
        }

        fieldset = (
            field
            for field in data.get_fields()
            if not 'computed' in field.metadata.get('tags', [])
        )

        data = {
            path: value_func[f.type.__name__](n)
            for n, f in enumerate(fieldset)
            if (path := f.metadata.get('path'))
        }

        d_old = old.DataStruct()
        d_new = new.DataStruct()
        for k, v in data.items():
            setattr(d_old, k, v)
            self.assertEquals(getattr(d_old, k), v)
            setattr(d_new, k, v)
            self.assertEquals(getattr(d_new, k), v)

        encoded_old = d_old.encode()
        encoded_new = d_new.encode()

        self.assertEquals(encoded_old, encoded_new)
