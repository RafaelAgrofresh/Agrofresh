import asyncio
import itertools as it
import json
import logging
import logging.config
import math
import os
import time
from cold_rooms.models import ColdRoom
from django.db.models.signals import post_save
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from historical.models import (
    Alarm,
    Parameter,
    Measurement,
    FloatData,
    IntegerData,
    BooleanData,
    Event,
    AlarmEvent,
    AcknowledgeAlarmsEvent,
    ParameterChangeEvent,
    ParameterChangeCommand,
)
from historical.signals import model_change as historical_model_change
from cold_rooms.signals import model_change as cold_rooms_model_change
from .signals import comms_start, comms_alarm, comms_error
from .mbus_types import (
    BYTEORDER, WORDORDER, EEPROM,
    u16, u32, i16, i32, f32,
)
from .structs import DataStruct
from .structs_common import tagged_as
from .tags import *
from asgiref.sync import sync_to_async
from dataclasses import asdict, dataclass, fields, is_dataclass
from django.db import transaction
from django.utils import timezone
from decorators import catch
from pymodbus.client.asynchronous import schedulers
from pymodbus.client.asynchronous.async_io import (
    init_tcp_client,
    ReconnectingAsyncioModbusTcpClient,
)
from pymodbus.constants import Defaults
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.pdu import ExceptionResponse
from wsockets import broadcast
from uuid import uuid4
import traceback


logger = logging.getLogger(__name__)
# TODO use confugured log_level
# TODO move print to logger.{info|debug|error}
# see https://docs.djangoproject.com/en/3.0/topics/logging/#examples
# log_errors = lambda name: catch(lambda e: logger.error(f"{name} - {e}"))
# log_errors = lambda name: catch(lambda e: logging.error('%s - %s', name, e, exc_info=e))
log_errors = lambda name: catch(lambda e: print(f"{name} - {e}", traceback.format_exc()))


@log_errors("mbus_block_read")
async def mbus_block_read(client, unit, address, count):
    # Because the number of bytes for register values is 8-bit wide and maximum modbus message
    # size is 256 bytes, only 125 registers for Modbus RTU and 123 registers for Modbus TCP
    # can be read at once
    MAX_SIZE = 123
    n_reads = math.ceil(count / MAX_SIZE)
    for n in range(n_reads):
        offset = n * MAX_SIZE
        length = MAX_SIZE if n + 1 < n_reads else count - offset
        rr = await client.read_holding_registers(
            unit=unit,
            address=address + offset,
            count=length)
        if isinstance(rr, ExceptionResponse):
            raise Exception(f"{rr} @ (unit: {unit}, address: {address + offset}, count: {length})")

        yield rr

@log_errors("mbus_block_write")
async def mbus_block_write(client, unit, address, values):
    # Because register values are 2-bytes wide and only 127 bytes worth of values can be sent,
    # only 63 holding registers can be preset/written at once.
    MAX_SIZE = 63
    n_writes = math.ceil(len(values) / MAX_SIZE)
    for n in range(n_writes):
        offset = n * MAX_SIZE
        length = MAX_SIZE if n + 1 < n_writes else len(values) - offset
        wr = await client.write_registers(
            unit=unit,
            address=address + offset,
            values=values[offset: offset + length])

        if isinstance(wr, ExceptionResponse):
            raise Exception(f"{wr} @ (unit: {unit}, address: {address + offset}, count: {length})")

        yield wr

@sync_to_async
def get_all(model):
    return [item for item in model.objects.all()]


class NotConnectedError(Exception): pass


@dataclass
class ColdRoomCommsClient:
    cold_room: ColdRoom = None
    mb_client: ReconnectingAsyncioModbusTcpClient = None
    data_struct: DataStruct = None
    data_struct_size: int = 0
    error: Exception = None
    messages = {}

    @log_errors("client_initialize")
    async def initialize(self):
        self.data_struct = DataStruct()
        self.data_struct_size = DataStruct.size()
        Defaults.Timeout = 1
        self.mb_client = await init_tcp_client(
            proto_cls=None,
            loop=asyncio.get_running_loop(),
            host=self.cold_room.host,
            port=self.cold_room.port,
            unit=self.cold_room.unit)

        # force not proportional mode
        # if proportional mode is disabled
        await self.read_data()

        if self.data_struct.CO2ControlSelection\
        and not self.cold_room.enable_CO2_proportional_ctrl:
            await self.write("CO2ControlSelection", False, None)

        if self.data_struct.C2H4ControlSelection\
        and not self.cold_room.enable_C2H4_proportional_ctrl:
            await self.write("C2H4ControlSelection", False, None)

    def get_base_addr(self):
        return self.cold_room.address % 40000

    def validate_connection(self):
        if not self.mb_client.connected:
            raise NotConnectedError(
                f"Could not connect to '{self.cold_room.name}' @ {self.cold_room.endpoint}"
            )

    def notify_error(func):
        async def wrapped(*args, **kwargs):
            self = args[0]
            prev_error = self.error
            result = await func(*args, **kwargs)
            if self.error and str(self.error) != str(prev_error):
                comms_error.send(
                    sender=self.__class__,
                    cold_room=self.cold_room,
                    error=self.error,
                )

            return result

        return wrapped

    def catch_error(func):
        async def wrapped(*args, **kwargs):
            self = args[0]
            try:
                result = await func(*args, **kwargs)
                self.error = None
                return result
            except asyncio.exceptions.TimeoutError as error:
                self.error = Exception(
                    f"Could not connect to '{self.cold_room.name}' @ {self.cold_room.endpoint}. TimeOut"
                )
            except Exception as error:
                self.error = error
                # raise error
        return wrapped

    @log_errors("client_read_data")
    @notify_error
    @catch_error
    async def read_data(self):
        self.validate_connection()

        length = self.data_struct_size
        offset = self.get_base_addr()
        reads = mbus_block_read(
            self.mb_client.protocol,
            self.cold_room.unit,
            offset, length)

        registers = [
            r
            async for read in reads
            for r in read.registers]

        assert length == len(registers), \
            f"Expected {length} registers, got {len(registers)}"

        self.data_struct.decode(registers)

    @log_errors("client_write_random_values")
    @notify_error
    @catch_error
    async def write_random_values(self):
        self.validate_connection()

        struct = DataStruct()
        struct.randomize()
        registers = struct.encode()
        offset = self.get_base_addr()
        writes = mbus_block_write(
            client=self.mb_client.protocol,
            unit=self.cold_room.unit,
            address=offset,
            values=registers)

        assert(all([
            response.function_code < 0x80
            async for response in writes]))

    @sync_to_async
    def save_param_change_command(self, path, value, user):
        param = Parameter.objects.get(name=path)
        event = ParameterChangeCommand(
            ts=timezone.now(),
            parameter=param,
            cold_room=self.cold_room,
            user=user.username if user else None,
            value=value)
        event.save()

    @log_errors("client_write")
    @notify_error
    @catch_error
    async def write(self, path, value, user):
        self.validate_connection()

        base    = self.get_base_addr()
        field   = self.data_struct.get_field(path)
        offset  = field.metadata.get('offset')
        encoder = BinaryPayloadBuilder(byteorder=BYTEORDER, wordorder=WORDORDER)

        # TODO write_command instead of param_change_command?
        if tagged_as(PARAM)(field):
            await self.save_param_change_command(path, value, user)

        if field.type == bool:
            assert isinstance(value, bool), \
                f"Expected '{bool.__name__}' value got {value}"

            rr = await self.mb_client.protocol.read_holding_registers(
                unit=self.cold_room.unit,
                address=base + offset,
                count=1)

            bit = field.metadata.get('bit')
            u16value = rr.registers[0]
            bits = [bool(u16value & (0x1 << k)) for k in range(16)]
            bits[bit] = value
            value = sum(0x1 << k for k, bit in enumerate(bits) if bit)
            encoder.add_16bit_uint(int(value))

        elif field.type in (u16, u32, i16, i32, f32):
            value = field.type(value)
            value._encode(encoder)

        else:
            raise TypeError(f"Invalid type '{field.type.__name__}'")

        registers = encoder.to_registers()
        print(f"Writing {registers} @ {self.cold_room.endpoint}+{offset}")
        response = await self.mb_client.protocol.write_registers(
            unit=self.cold_room.unit,
            address=base + offset,
            values=registers)

        # assert response.function_code < 0x80, \
        #     f"Write error when writing {registers} @ {self.cold_room.address + offset}"

        result = response.function_code < 0x80

        if isinstance(field, EEPROM):
            result &= bool(await self._write_to_epprom(field.type, offset))

        return result

    @log_errors("client__write_to_eeprom")
    async def _write_to_epprom(self, ftype, offset):
        base    = self.get_base_addr()
        eeprom  = self.data_struct.get_field("eepromTypeToSave")
        encoder = BinaryPayloadBuilder(byteorder=BYTEORDER, wordorder=WORDORDER)

        if ftype == bool:
            encoder.add_16bit_uint(1)

        elif ftype in (u16, i16):
            encoder.add_16bit_uint(1)

        elif ftype in (f32, u32, i32):
            encoder.add_16bit_uint(2)

        else:
            raise TypeError(f"Invalid type '{field.type.__name__}'")

        encoder.add_16bit_uint(offset)
        registers = encoder.to_registers()

        # TODO generate event log
        print(f"Writing to eeprom {ftype.__name__} @ {offset} -> {registers} @ eepromTypeToSave")
        response = await self.mb_client.protocol.write_registers(
            unit=self.cold_room.unit,
            address=base + eeprom.metadata.get('offset'),
            values=registers)

        # assert response.function_code < 0x80, \
        #     f"Write error when writing {registers} @ {self.cold_room.address + offset}"

        return response.function_code < 0x80

    def get_struct(self):
        struct = {
            "cold_room": self.cold_room.id,
            # "cold_room": model_to_dict(client.cold_room, fields=("id", "name"))
            **self.data_struct.asdict(),
        }

        if self.error:
            struct = {
                'error': str(self.error),
                **struct
            }

        return struct

    @log_errors("client__apply_constraints")
    async def apply_constraints(self):
        if not self.cold_room.enable_CO2_proportional_ctrl \
        and self.data_struct.CO2ControlSelection:
            # proprotional option is not enabled
            await self.write("CO2ControlSelection", False, None)

        if not self.cold_room.enable_C2H4_proportional_ctrl \
        and self.data_struct.C2H4ControlSelection:
            # proprotional option is not enabled
            await self.write("C2H4ControlSelection", False, None)

    def get_messages(self):
        # TODO improve (rule system)
        posedge = self.data_struct.posedge
        cold_room = model_to_dict(self.cold_room, fields=("id", "name"))

        if posedge.finalInjectionMessageActivated:
            if self.data_struct.start1 and not self.data_struct.start2:
                self.messages["finalInjectionMessageActivated"] = {
                    "cls": "confirm",
                    "msg": str(_("Fin de inyección inicial de etileno.")) + "\n"
                        + str(_("¿Iniciar el control por balance de gases?")),
                    "yes": { "finalInjectionMessageActivated": False, "start1": False, "start2": True },
                    "no": { "finalInjectionMessageActivated": False, "start1": False, "start2": False },
                    "log": False,
                }

            elif self.data_struct.start1 and self.data_struct.start2:
                self.messages["finalInjectionMessageActivated"] = {
                    "cls": "notify",
                    "msg": _("Fin de inyección inicial de etileno"),
                    "log": False,
                }

        if posedge.C2H4LowPressureAlarm:
            self.messages["C2H4LowPressureAlarm"] = {
                "cls": "notify",
                "msg": _("Nivel bajo de Etileno, es necesario cambiar las botellas de etileno"),
                "log": True,
            }

        if posedge.emergencyStopState:
            self.messages["emergencyStopState"] = {
                "cls": "notify",
                "msg": _("Seta de emergencia pulsada"),
                "log": True,
            }

        if posedge.manualPowerCutMessage:
            self.messages["manualPowerCutMessage"] = {
                "cls": "notify",
                "msg": _("Interruptor manual de corte de corriente activado"),
                "log": True,
            }

        if posedge.powerOutage:
            self.messages["powerOutage"] = {
                "cls": "notify",
                "msg": _("Corte de corriente"),
                "log": False,
            }

        # TODO log? define as IODATA and enable

        return [
            {**v, "id": k, "src": cold_room}
            for k, v in self.messages.items()
        ]

    def accept_message(self, msg_id):
        if not msg_id in self.messages:
            return False

        del self.messages[msg_id]
        return True


# TODO SRP (use django signals?)
class CommsEngine:
    def __init__(self):
        self.clients = []
        self.alarms  = []
        self.params  = []
        self.restart_required = False

    @log_errors("CommsEngine")
    async def __call__(self, period=2):
        await self.initialize()
        logger.info(f'Starting periodic task...')
        comms_start.send(sender=self.__class__)
        while True:
            if self.restart_required:
                logger.info(f'Restarting comms ...')
                await self.initialize()

            t0 = time.perf_counter()
            # await self.write_random_values()
            await self.read_data()
            await self.ws_broadcast()
            await self.save_historical_data()
            await self.apply_constraints()
            elapsed_time = time.perf_counter() - t0
            logger.info(f'{t0:0.4f} periodic comms (elapsed time: {elapsed_time:0.4f})')
            await asyncio.sleep(period - elapsed_time)

    @log_errors("initialize")
    async def initialize(self):
        cold_rooms = await get_all(ColdRoom)
        self.clients = [
            ColdRoomCommsClient(cold_room)
            for cold_room in cold_rooms
        ]

        tasks = (client.initialize() for client in self.clients)
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.initialize_db()

        # preload db data
        self.alarms = await get_all(Alarm)
        self.params = await get_all(Parameter)
        self.measurements = await get_all(Measurement)

        self.restart_required = False
        cold_rooms_model_change.connect(self.restart_comms)
        historical_model_change.connect(self.sync_data)
        post_save.connect(self.notify_event, sender=Event)

    def notify_event(self, *args, **kwargs):
        event = kwargs.get('instance')
        if event.type == 'AlarmEvent' and event.value is True:
            comms_alarm.send(sender=self.__class__, alarm=event)

    def restart_comms(self, sender, model, **kwargs):
        self.restart_required = True

    def sync_data(self, sender, model, **kwargs):
        # TODO improve
        if not isinstance(model, (Alarm, Parameter, Measurement)):
            return

        if isinstance(model, Alarm):
            self.alarms = [
                model if alarm.id == model.id else alarm
                for alarm in self.alarms
            ]
            return

        if isinstance(model, Parameter):
            self.params = [
                model if param.id == model.id else param
                for param in self.params
            ]
            return

        if isinstance(model, Measurement):
            self.measurements = [
                model if measurement.id == model.id else measurement
                for measurement in self.measurements
            ]
            return

        raise NotImplementedError()

    @log_errors("initialize_db")
    async def initialize_db(self):
        tasks = [
            # update LUTs used as FK
            sync_to_async(Alarm.update)(),
            sync_to_async(Parameter.update)(),
            sync_to_async(Measurement.update)(),
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    @log_errors("write_random_values")
    async def write_random_values(self):
        tasks = (client.write_random_values() for client in self.clients)
        await asyncio.gather(*tasks, return_exceptions=True)

    @log_errors("read_data")
    async def read_data(self):
        tasks = (client.read_data() for client in self.clients)
        await asyncio.gather(*tasks, return_exceptions=True)

    @sync_to_async
    def get_not_ack_alarms(self):
        from django.forms.models import model_to_dict
        not_ack_alarms = (
            Event.alarms.get_unacknowledged_alarms()
            # .values('meta', 'ts', 'ts_end', 'ts_ack')
        )
        not_ack_alarms = [
            {
                'meta': alarm.meta,
                'ts': alarm.ts,
                'ts_end': alarm.ts_end,
                'ts_ack': alarm.ts_ack,
                'active': alarm.active,
                'ack': alarm.ack,
                'name': next(a.name for a in self.alarms if a.pk == alarm.meta['alarm'])
            }
            # model_to_dict(alarm)
            for alarm in not_ack_alarms
        ]
        return list(not_ack_alarms)

    def get_messages(self):
        return [
            msg
            for client in self.clients
            for msg in client.get_messages()
        ]

    @log_errors("ws_broadcast")
    async def ws_broadcast(self):
        payload = {
            "structs": [
                client.get_struct()
                for client in self.clients
            ],
            "alarms": await self.get_not_ack_alarms(),
            "messages": self.get_messages()
        }

        await broadcast(payload)

    @log_errors("save_historical_data")
    async def save_historical_data(self):
        alarms = self.get_alarm_events()
        params = self.get_param_change_events()
        events = it.chain(alarms, params)

        await asyncio.gather(
            self.save_measurements(),
            self.save_events(events),
            return_exceptions=True)

    # TODO atomic transactions not needed
    # filter out changed SaveOnChange instances
    # use bulk insert
    @sync_to_async
    @log_errors("save_measurements")
    def save_measurements(self):
        type_tables_LUT = [
            (Measurement.Type.FLOAT,  FloatData, True),
            (Measurement.Type.INT,  IntegerData, True),
            # Boolean -> SaveOnValueChangeMixin not working with bulk_create
            (Measurement.Type.BOOL, BooleanData, False),
        ]

        ts = timezone.now()
        for mtype, model, bulk in type_tables_LUT:
            models = (
                model(**{
                    "ts": ts,
                    "measurement": measurement,
                    "cold_room": client.cold_room,
                    "value": getattr(client.data_struct, measurement.name)
                })
                for client in self.clients
                for measurement in self.measurements
                if measurement.type == mtype
                    and client.error is None
                    and measurement.enabled
                    and hasattr(client.data_struct, measurement.name)
            )

            if bulk:
                # bulk insert
                model.objects.bulk_create(models)

            else:
                with transaction.atomic():
                    for event in models:
                        event.save()

    @sync_to_async
    @log_errors("save_events")
    def save_events(self, events):
        with transaction.atomic():
            for event in events:
                event.save()

    def get_alarm_events(self):
        ts = timezone.now()
        yield from (
            AlarmEvent(
                ts=ts,
                alarm=alarm,
                cold_room=client.cold_room,
                value=getattr(client.data_struct, alarm.name))
            for client in self.clients
            for alarm in self.alarms
            if hasattr(client.data_struct, alarm.name) # FIXME nested alarms
                and client.error is None
                and alarm.enabled
        )

    def get_param_change_events(self):
        ts = timezone.now()
        yield from (
            ParameterChangeEvent(
                ts=ts,
                parameter=param,
                cold_room=client.cold_room,
                value=getattr(client.data_struct, param.name))
            for client in self.clients
            for param in self.params
            if hasattr(client.data_struct, param.name) # FIXME nested params
                and client.error is None
                and param.enabled
        )

    @log_errors("apply_constraints")
    async def apply_constraints(self):
        tasks = (client.apply_constraints() for client in self.clients)
        await asyncio.gather(*tasks, return_exceptions=True)


mbus = CommsEngine()

# def exception_handler(loop, context):
#     logger.error(f"Caught exception: {context['exception']}")

# mbus = CommsEngine()
# loop = asyncio.get_event_loop()
# # loop.set_exception_handler(exception_handler)
# task = loop.create_task(mbus(period=0.5))

# if __name__ == "__main__":
#     logging.basicConfig()
#     logger.setLevel(logging.INFO)
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(task)
#     loop.close()
