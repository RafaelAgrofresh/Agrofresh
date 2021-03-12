from dataclasses import (
    # _is_dataclass_instance,
    dataclass,
    field,
    # fields,
    # is_dataclass,
)
from django.utils.translation import gettext_noop as _
from pymodbus.payload import (
    BinaryPayloadBuilder,
    BinaryPayloadDecoder,
)
from .mbus_types import (
    MemMapped,
    EEPROM,
)
from .mbus_types_old import (
    MBusSerializable,
    i16, i32, u16, u32, f32,
)
from .structs_common import (
    clamp,
    to_bits,
    from_bits,
)
from .tags import *
import math


@dataclass
class PIDControllerParams(MBusSerializable):
    pCoefficient: i16 = EEPROM.new(default=0, metadata={'description': _('Ganancia proporcional')})
    iCoefficient: i16 = EEPROM.new(default=0, metadata={'description': _('Ganancia integral')})
    dCoefficient: i16 = EEPROM.new(default=0, metadata={'description': _('Ganancia derivativa')})
    # reference: i16  = EEPROM.new(default=0, metadata={'description': _('Referencia'), 'tags': [PARAM]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_int(self.pCoefficient) # uint ??
        encoder.add_16bit_int(self.iCoefficient) # uint ??
        encoder.add_16bit_int(self.dCoefficient) # uint ??
        # encoder.add_16bit_int(self.reference)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.pCoefficient = decoder.decode_16bit_int() # uint ??
        self.iCoefficient = decoder.decode_16bit_int() # uint ??
        self.dCoefficient = decoder.decode_16bit_int() # uint ??
        # self.reference    = decoder.decode_16bit_int()

@dataclass
class SensorParams(MBusSerializable):
    units: str   = field(default='', metadata={'description': _('Unidades de sensor')})

    # rango
    minimum: i16 = EEPROM.new(default=0, metadata={'description': _('Mínimo rango sensor')})
    maximum: i16 = EEPROM.new(default=0, metadata={'description': _('Máximo rango sensor')})

    # calibración
    zero: i16 = EEPROM.new(default=0, metadata={'description': _('Ajuste zero sensor')})
    span: i16 = EEPROM.new(default=0, metadata={'description': _('Ajuste span sensor')})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_int(self.minimum)
        encoder.add_16bit_int(self.maximum)
        encoder.add_16bit_int(self.zero)
        encoder.add_16bit_int(self.span)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.minimum = decoder.decode_16bit_int()
        self.maximum = decoder.decode_16bit_int()
        self.zero    = decoder.decode_16bit_int()
        self.span    = decoder.decode_16bit_int()

@dataclass
class DateTime(MBusSerializable):
    year   : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (año)')})
    month  : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (mes)')})
    day    : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (día)')})
    hour   : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (hora)')})
    minute : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (min)')})
    second : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (sec)')})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(self.year)
        encoder.add_16bit_uint(self.month)
        encoder.add_16bit_uint(self.day)
        encoder.add_16bit_uint(self.hour)
        encoder.add_16bit_uint(self.minute)
        encoder.add_16bit_uint(self.second)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.year   = decoder.decode_16bit_uint()
        self.month  = decoder.decode_16bit_uint()
        self.day    = decoder.decode_16bit_uint()
        self.hour   = decoder.decode_16bit_uint()
        self.minute = decoder.decode_16bit_uint()
        self.second = decoder.decode_16bit_uint()

    @property
    def datetime(self):
        return datetime(
            year   = self.year,
            month  = self.month,
            day    = self.day,
            hour   = self.hour,
            minute = self.minute,
            second = self.second)

    @datetime.setter
    def datetime(self, value):
        self.year   = value.year
        self.month  = value.month
        self.day    = value.day
        self.hour   = value.hour
        self.minute = value.minute
        self.second = value.second


@dataclass
class Block00(MBusSerializable):
    onOffSystem            : bool = EEPROM.new(default=False, metadata={'description': _('Paro/marcha cámara'),                         'tags': [PARAM, SYSTEM]})
    workingMode            : bool = EEPROM.new(default=False, metadata={'description': _('Modo trabajo (conservación/desverdización)'), 'tags': [PARAM, SYSTEM]})
    start2                 : bool = EEPROM.new(default=False, metadata={'description': _('Inicio de ciclo(conservación/desverdizado)'), 'tags': [IODATA, C2H4, GAS_BALANCE]})
    powerOutage            : bool = EEPROM.new(default=False, metadata={'description': _('Detección microcortes'),                      'tags': [PARAM, ALARM_CFG]}) # alarm?
    C2H4ControlSelection   : bool = EEPROM.new(default=False, metadata={'description': _('Selección control etileno (analisis/balance de gases)'), 'tags': [PARAM, C2H4]})
    CO2ControlSelection    : bool = EEPROM.new(default=False, metadata={'description': _('Selección control CO2 (pid/consigna)'),                  'tags': [PARAM, CO2]})
    warmControlSelection   : bool = EEPROM.new(default=False, metadata={'description': _('Selección control calor (agrofresh/externo)'),           'tags': [PARAM, TEMPERATURE]})
    coldControlSelection   : bool = EEPROM.new(default=False, metadata={'description': _('Selección control frío (agrofresh/externo)'),            'tags': [PARAM, TEMPERATURE]})
    outsideTempAvailable   : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado control temperatura equipo externo'),         'tags': [PARAM, TEMPERATURE]})
    humidityNozzleEnable1  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla humedad 1'),                         'tags': [PARAM, HUMIDITY]})
    humidityNozzleEnable2  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla humedad 2'),                         'tags': [PARAM, HUMIDITY]})
    humidityNozzleEnable3  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla humedad 3'),                         'tags': [PARAM, HUMIDITY]})
    humidityNozzleEnable4  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla humedad 4'),                         'tags': [PARAM, HUMIDITY]})
    humidityNozzleEnable5  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla humedad 5'),                         'tags': [PARAM, HUMIDITY]})
    humidityNozzleEnable6  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla humedad 6'),                         'tags': [PARAM, HUMIDITY]})
    humidityNozzleEnable7  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla humedad 7'),                         'tags': [PARAM, HUMIDITY]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.onOffSystem,
            self.workingMode,
            self.start2,
            self.powerOutage,
            self.C2H4ControlSelection,
            self.CO2ControlSelection,
            self.warmControlSelection,
            self.coldControlSelection,
            self.outsideTempAvailable,
            self.humidityNozzleEnable1,
            self.humidityNozzleEnable2,
            self.humidityNozzleEnable3,
            self.humidityNozzleEnable4,
            self.humidityNozzleEnable5,
            self.humidityNozzleEnable6,
            self.humidityNozzleEnable7,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.onOffSystem           = flags[0]
        self.workingMode           = flags[1]
        self.start2                = flags[2]
        self.powerOutage           = flags[3]
        self.C2H4ControlSelection  = flags[4]
        self.CO2ControlSelection   = flags[5]
        self.warmControlSelection  = flags[6]
        self.coldControlSelection  = flags[7]
        self.outsideTempAvailable  = flags[8]
        self.humidityNozzleEnable1 = flags[9]
        self.humidityNozzleEnable2 = flags[10]
        self.humidityNozzleEnable3 = flags[11]
        self.humidityNozzleEnable4 = flags[12]
        self.humidityNozzleEnable5 = flags[13]
        self.humidityNozzleEnable6 = flags[14]
        self.humidityNozzleEnable7 = flags[15]

@dataclass
class Block01(MBusSerializable):
    humidityNozzleEnable8  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla humedad 8'),         'tags': [PARAM, HUMIDITY]})
    C2H4SystemOn1          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado equipo etileno 1'),           'tags': [PARAM, C2H4]})
    inFanOn                : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador entrada'),         'tags': [PARAM, CO2]})
    outFanOn               : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador salida'),          'tags': [PARAM, CO2]})
    openDoorOn1            : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma puerta abierta 1'),    'tags': [PARAM, C2H4, GAS_BALANCE]})
    openDoorOn2            : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma puerta abierta 2'),    'tags': [PARAM, C2H4, GAS_BALANCE]})
    highTemperatureOnAlarm : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma alta temperatura'),    'tags': [PARAM, ALARM_CFG]})
    lowTemperatureOnAlarm  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma baja temperatura'),    'tags': [PARAM, ALARM_CFG]})
    highHumedadOnAlarm     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma alta humedad'),        'tags': [PARAM, ALARM_CFG]})
    lowHumedadOnAlarm      : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma baja humedad'),        'tags': [PARAM, ALARM_CFG]})
    highC2H4OnAlarm        : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma alto etileno'),        'tags': [PARAM, ALARM_CFG]})
    lowC2H4OnAlarm         : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma bajo etileno'),        'tags': [PARAM, ALARM_CFG]})
    highCO2OnAlarm         : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma alto CO2'),            'tags': [PARAM, ALARM_CFG]})
    noVentilationOnAlarm   : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma ausencia ventilación'),'tags': [PARAM, ALARM_CFG]})
    _reserved_01_14        : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 14'),                       'tags': [RESERVED]})
    _reserved_01_15        : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 15'),                       'tags': [RESERVED]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.humidityNozzleEnable8,
            self.C2H4SystemOn1,
            self.inFanOn,
            self.outFanOn,
            self.openDoorOn1,
            self.openDoorOn2,
            self.highTemperatureOnAlarm,
            self.lowTemperatureOnAlarm,
            self.highHumedadOnAlarm,
            self.lowHumedadOnAlarm,
            self.highC2H4OnAlarm,
            self.lowC2H4OnAlarm,
            self.highCO2OnAlarm,
            self.noVentilationOnAlarm,
            False, # self._reserved_01_14
            False, # self._reserved_01_15
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.humidityNozzleEnable8  = flags[0]
        self.C2H4SystemOn1          = flags[1]
        self.inFanOn                = flags[2]
        self.outFanOn               = flags[3]
        self.openDoorOn1            = flags[4]
        self.openDoorOn2            = flags[5]
        self.highTemperatureOnAlarm = flags[6]
        self.lowTemperatureOnAlarm  = flags[7]
        self.highHumedadOnAlarm     = flags[8]
        self.lowHumedadOnAlarm      = flags[9]
        self.highC2H4OnAlarm        = flags[10]
        self.lowC2H4OnAlarm         = flags[11]
        self.highCO2OnAlarm         = flags[12]
        self.noVentilationOnAlarm   = flags[13]
        # self._reserved_01_14        = flags[14]
        # self._reserved_01_15        = flags[15]

@dataclass
class Block02(MBusSerializable):
    airNozzleEnable1  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire 1'),           'tags': [PARAM, HUMIDITY]})
    airNozzleEnable2  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire 2'),           'tags': [PARAM, HUMIDITY]})
    airNozzleEnable3  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire 3'),           'tags': [PARAM, HUMIDITY]})
    airNozzleEnable4  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire 4'),           'tags': [PARAM, HUMIDITY]})
    airNozzleEnable5  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire 5'),           'tags': [PARAM, HUMIDITY]})
    airNozzleEnable6  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire 6'),           'tags': [PARAM, HUMIDITY]})
    airNozzleEnable7  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire 7'),           'tags': [PARAM, HUMIDITY]})
    airNozzleEnable8  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire 8'),           'tags': [PARAM, HUMIDITY]})
    manualPowerCut    : bool = EEPROM.new(default=False, metadata={'description': _('Flag de corte de alimentación manual'), 'tags': [PARAM, SYSTEM]})
    _reserved_02_09   : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 09'),                      'tags': [RESERVED]})
    _reserved_02_10   : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 10'),                      'tags': [RESERVED]})
    _reserved_02_11   : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 11'),                      'tags': [RESERVED]})
    _reserved_02_12   : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 12'),                      'tags': [RESERVED]})
    _reserved_02_13   : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 13'),                      'tags': [RESERVED]})
    _reserved_02_14   : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 14'),                      'tags': [RESERVED]})
    _reserved_02_15   : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 15'),                      'tags': [RESERVED]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.airNozzleEnable1,
            self.airNozzleEnable2,
            self.airNozzleEnable3,
            self.airNozzleEnable4,
            self.airNozzleEnable5,
            self.airNozzleEnable6,
            self.airNozzleEnable7,
            self.airNozzleEnable8,
            self.manualPowerCut,
            False, # self._reserved_02_09,
            False, # self._reserved_02_10,
            False, # self._reserved_02_11,
            False, # self._reserved_02_12,
            False, # self._reserved_02_13,
            False, # self._reserved_02_14,
            False, # self._reserved_02_15,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.airNozzleEnable1 = flags[0]
        self.airNozzleEnable2 = flags[1]
        self.airNozzleEnable3 = flags[2]
        self.airNozzleEnable4 = flags[3]
        self.airNozzleEnable5 = flags[4]
        self.airNozzleEnable6 = flags[5]
        self.airNozzleEnable7 = flags[6]
        self.airNozzleEnable8 = flags[7]
        self.manualPowerCut   = flags[8]
        # self._reserved_02_09  = flags[9]
        # self._reserved_02_10  = flags[10]
        # self._reserved_02_11  = flags[11]
        # self._reserved_02_12  = flags[12]
        # self._reserved_02_13  = flags[13]
        # self._reserved_02_14  = flags[14]
        # self._reserved_02_15  = flags[15]


@dataclass
class Block03(MBusSerializable):
    CO2PIDMin                : u16 = EEPROM.new(default=0, metadata={'description': _('Consigna mínimo PID CO2'),                       'tags': [PARAM, SETTINGS, PID, CO2]})
    CO2PIDMax                : u16 = EEPROM.new(default=0, metadata={'description': _('Consigna máximo PID CO2'),                       'tags': [PARAM, SETTINGS, PID, CO2]})
    C2H4PIDMin               : u16 = EEPROM.new(default=0, metadata={'description': _('Consigna mínimo PID Etileno'),                   'tags': [PARAM, SETTINGS, PID, C2H4]})
    C2H4PIDMax               : u16 = EEPROM.new(default=0, metadata={'description': _('Consigna máximo PID Etileno'),                   'tags': [PARAM, SETTINGS, PID, C2H4]})
    C2H4FlowPIDMin           : u16 = EEPROM.new(default=0, metadata={'description': _('Consigna mínimo PID Flujo Etileno'),             'tags': [PARAM, SETTINGS, PID, C2H4]})
    C2H4FlowPIDMax           : u16 = EEPROM.new(default=0, metadata={'description': _('Consigna máximo PID Flujo Etileno'),             'tags': [PARAM, SETTINGS, PID, C2H4]})

    modbusOffSet             : u16 = EEPROM.new(default=0, metadata={'description': _('Offset de los registros'),                       'tags': [PARAM, SETTINGS]})
    chamberVolume            : u16 = EEPROM.new(default=0, metadata={'description': _('Volumen de la cámara'),                          'tags': [PARAM, C2H4, GAS_BALANCE]})
    extractionHysteresis     : u16 = EEPROM.new(default=0, metadata={'description': _('Histéresis modo clásico extracción'),            'tags': [PARAM, CO2]})
    C2H4GasConcentration     : u32 = EEPROM.new(default=0, metadata={'description': _('Concentración de la mezcla de gas etileno'),     'tags': [PARAM, C2H4, GAS_BALANCE]})

    refHumidity              : f32 = EEPROM.new(default=0.0, metadata={'units': '%',   'description': _('Consigna humedad'),            'tags': [PARAM, BASIC, HUMIDITY]})
    refTemperature           : f32 = EEPROM.new(default=0.0, metadata={'units': 'ºC',  'description': _('Consigna temperatura'),        'tags': [PARAM, BASIC, TEMPERATURE]})
    refC2H4                  : f32 = EEPROM.new(default=0.0, metadata={'units': 'ppm', 'description': _('Consigna etileno'),            'tags': [PARAM, BASIC, C2H4]})
    lowRefCO2                : u16 = EEPROM.new(default=0,   metadata={'units': 'ppm', 'description': _('Consigna inferior CO2'),       'tags': [PARAM, BASIC, CO2]})
    highRefCO2               : u16 = EEPROM.new(default=0,   metadata={'units': 'ppm', 'description': _('Consigna superior CO2'),       'tags': [PARAM, BASIC, CO2]})
    lowerBandTempStartUpHeat : f32 = EEPROM.new(default=0.0, metadata={'units': 'ºC',  'description': _('Banda inferior temperatura puesta en marcha calor'), 'tags': [PARAM, TEMPERATURE]})
    upperBandTempStartUpCold : f32 = EEPROM.new(default=0.0, metadata={'units': 'ºC',  'description': _('Banda superior temperatura puesta en marcha frio'),  'tags': [PARAM, TEMPERATURE]})
    lowerBandTempStopHeat    : f32 = EEPROM.new(default=0.0, metadata={'units': 'ºC',  'description': _('Banda inferior temperatura paro calor'),             'tags': [PARAM, TEMPERATURE]})
    upperBandTempStopCold    : f32 = EEPROM.new(default=0.0, metadata={'units': 'ºC',  'description': _('Banda superior temperatura paro frio'),              'tags': [PARAM, TEMPERATURE]})
    spHighTemperatureAlarm   : f32 = EEPROM.new(default=0.0, metadata={'units': 'ºC',  'description': _('Setpoint alarma alta temperatura'),                  'tags': [PARAM, BASIC, ALARM_CFG, TEMPERATURE]})
    spLowTemperatureAlarm    : f32 = EEPROM.new(default=0.0, metadata={'units': 'ºC',  'description': _('Setpoint alarma baja temperatura'),                  'tags': [PARAM, BASIC, ALARM_CFG, TEMPERATURE]})
    spHighHumidityAlarm      : f32 = EEPROM.new(default=0.0, metadata={'units': '%',   'description': _('Setpoint alarma alta humedad'),                      'tags': [PARAM, BASIC, ALARM_CFG, HUMIDITY]})
    spLowHumidityAlarm       : f32 = EEPROM.new(default=0.0, metadata={'units': '%',   'description': _('Setpoint alarma baja humedad'),                      'tags': [PARAM, BASIC, ALARM_CFG, HUMIDITY]})
    spHighC2H4Alarm          : f32 = EEPROM.new(default=0.0, metadata={'units': 'ppm', 'description': _('Setpoint alarma alto etileno'),                      'tags': [PARAM, BASIC, ALARM_CFG, C2H4]})
    spLowC2H4Alarm           : f32 = EEPROM.new(default=0.0, metadata={'units': 'ppm', 'description': _('Setpoint alarma bajo etileno'),                      'tags': [PARAM, BASIC, ALARM_CFG, C2H4]})
    spHighCO2Alarm           : u16 = EEPROM.new(default=0,   metadata={'units': 'ppm', 'description': _('Setpoint alarma alto CO2'),                          'tags': [PARAM, BASIC, ALARM_CFG, CO2]})
    pidHumidity              : PIDControllerParams = field(default_factory=lambda: PIDControllerParams(), metadata={'description': _('Constantes regulador PID humedad'), 'tags': [PARAM, PID, HUMIDITY]})
    pidCold                  : PIDControllerParams = field(default_factory=lambda: PIDControllerParams(), metadata={'description': _('Constantes regulador PID frío'),    'tags': [PARAM, PID, TEMPERATURE]})
    pidWarm                  : PIDControllerParams = field(default_factory=lambda: PIDControllerParams(), metadata={'description': _('Constantes regulador PID calor'),   'tags': [PARAM, PID, TEMPERATURE]})
    pidCO2                   : PIDControllerParams = field(default_factory=lambda: PIDControllerParams(), metadata={'description': _('Constantes regulador PID CO2'),     'tags': [PARAM, PID, CO2]})
    pidC2H4                  : PIDControllerParams = field(default_factory=lambda: PIDControllerParams(), metadata={'description': _('Constantes regulador PID C2H4'),    'tags': [PARAM, PID, C2H4]})
    C2H4SensorTime               : u16 = EEPROM.new(default=0, metadata={'units': 'sec',   'description': _('Tiempo reacción sensor etileno alarma'),             'tags': [PARAM, ALARM_CFG, C2H4]})
    initialInjection             : u16 = EEPROM.new(default=0, metadata={'units': 'sec',   'description': _('Tiempo de inyección inicial por balance de gases'),  'tags': [PARAM, C2H4, GAS_BALANCE]})
    intervalInjection            : u16 = EEPROM.new(default=0, metadata={'units': 'sec',   'description': _('Tiempo intervalo inyección por fugas'),              'tags': [PARAM, C2H4, GAS_BALANCE]})
    durationInjection            : u16 = EEPROM.new(default=0, metadata={'units': 'sec',   'description': _('Tiempo duración inyección por fugas'),               'tags': [PARAM, C2H4, GAS_BALANCE]})
    doorInjection                : u16 = EEPROM.new(default=0, metadata={'units': 'sec',   'description': _('Tiempo de inyección detección puerta'),              'tags': [PARAM, C2H4, GAS_BALANCE]})
    preColdHumidityInjectionTime : u16 = EEPROM.new(default=0, metadata={'units': 'sec',   'description': _('Tiempo de inyección antes de activar frío'),         'tags': [PARAM, HUMIDITY]})
    C2H4PressureSensor       : SensorParams = field(default_factory=lambda: SensorParams(units='ppm'), metadata={'description': _('Configuración sensor C2H4PressureSensor'), 'tags': [PARAM, SENSOR, C2H4]})
    continuouscCO2Threshold  : f32 = EEPROM.new(default=0, metadata={'units': '--',  'description': _('Treshold CO2'),                               'tags': [PARAM, PID, CO2]})
    C2H4PressureMin          : u16 = EEPROM.new(default=0, metadata={'units': '--',  'description': _('Alarma de poca presión de etileno'),          'tags': [PARAM, C2H4]})
    timeNoVentilationAlarm   : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo alarma ausencia ventilación'),         'tags': [PARAM, ALARM_CFG]})
    openDoorTimeAlarm1       : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo alarma puerta abierta 1'),             'tags': [PARAM, ALARM_CFG]})
    openDoorTimeAlarm2       : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo alarma puerta abierta 2'),             'tags': [PARAM, ALARM_CFG]})
    delayTimeStop            : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo retardo parada ventilador aerotermo'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})

    temperatureSensor1  : SensorParams = field(default_factory=lambda: SensorParams(units='ºC'),  metadata={'description': _('Configuración sensor temperatureSensor1'), 'tags': [PARAM, SENSOR, TEMPERATURE]})
    humiditySensor1     : SensorParams = field(default_factory=lambda: SensorParams(units='HR%'), metadata={'description': _('Configuración sensor humiditySensor1'),    'tags': [PARAM, SENSOR, HUMIDITY]})
    C2H4Sensor1         : SensorParams = field(default_factory=lambda: SensorParams(units='ppm'), metadata={'description': _('Configuración sensor C2H4Sensor1'),        'tags': [PARAM, SENSOR, C2H4]})
    CO2Sensor1          : SensorParams = field(default_factory=lambda: SensorParams(units='ppm'), metadata={'description': _('Configuración sensor CO2Sensor1'),         'tags': [PARAM, SENSOR, CO2]})
    temperatureSensor2  : SensorParams = field(default_factory=lambda: SensorParams(units='ºC'),  metadata={'description': _('Configuración sensor temperatureSensor2'), 'tags': [PARAM, SENSOR, TEMPERATURE]})
    humiditySensor2     : SensorParams = field(default_factory=lambda: SensorParams(units='HR%'), metadata={'description': _('Configuración sensor humiditySensor2'),    'tags': [PARAM, SENSOR, HUMIDITY]})
    C2H4Sensor2         : SensorParams = field(default_factory=lambda: SensorParams(units='ppm'), metadata={'description': _('Configuración sensor C2H4Sensor2'),        'tags': [PARAM, SENSOR, C2H4]})
    CO2Sensor2          : SensorParams = field(default_factory=lambda: SensorParams(units='ppm'), metadata={'description': _('Configuración sensor CO2Sensor2'),         'tags': [PARAM, SENSOR, CO2]})

    temperatureOutsideSensor1 : SensorParams = field(default_factory=lambda: SensorParams(units='ºC'),  metadata={'description': _('Configuración sensor temperatureOutsideSensor1'), 'tags': [PARAM, SENSOR, TEMPERATURE]})
    humidityOutsideSensor1    : SensorParams = field(default_factory=lambda: SensorParams(units='HR%'), metadata={'description': _('Configuración sensor humidityOutsideSensor1'),    'tags': [PARAM, SENSOR, HUMIDITY]})
    C2H4FlowSensor1           : SensorParams = field(default_factory=lambda: SensorParams(units='ppm'), metadata={'description': _('Configuración sensor C2H4FlowSensor1'),           'tags': [PARAM, SENSOR, C2H4]})
    ethylenePressureMin       : u16 = EEPROM.new(default=0,   metadata={'description': _('Mensaje de poca presión etileno'), 'tags': [PARAM, C2H4]})
    waterPressureMin          : u16 = EEPROM.new(default=0,   metadata={'description': _('Alarma de poca presión agua'),     'tags': [PARAM, SENSOR, HUMIDITY]})
    airPressureMin            : u16 = EEPROM.new(default=0,   metadata={'description': _('Alarma de poca presión aire'),     'tags': [PARAM, SENSOR, HUMIDITY]})
    ethyleneValueMin          : f32 = EEPROM.new(default=0.0, metadata={'description': _('Valor minimo mostrado'),           'tags': [PARAM, C2H4]})
    ethyleneBarrido           : f32 = EEPROM.new(default=0.0, metadata={'description': _('Barrido etileno'),                 'tags': [IODATA, TEMPERATURE]})
    timerBarrido              : u16 = EEPROM.new(default=0,   metadata={'description': _('Timer Barrido'),                   'tags': [IODATA, TEMPERATURE]})
    analogWaterPressureSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'),  metadata={'description': _('Configuración sensor analogWaterPressureSensor'), 'tags': [PARAM, SENSOR, HUMIDITY]})
    analogAirPressureSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'),  metadata={'description': _('Configuración sensor analogAirPressureSensor'),   'tags': [PARAM, SENSOR, HUMIDITY]})

    kFactorW                    : u16 = EEPROM.new(default=0,   metadata={'units': 'pulsos/litro', 'description': _('Factor k sensor caudal agua'),    'tags': [PARAM, SENSOR, HUMIDITY]})
    kFactorE                    : u16 = EEPROM.new(default=0,   metadata={'units': 'pulsos/litro', 'description': _('Factor k sensor caudal etileno'), 'tags': [PARAM, SENSOR, C2H4, GAS_BALANCE]})
    continuousHumidityThreshold : f32 = EEPROM.new(default=0.0, metadata={'description': _('% error para marcha continua humedad'),      'tags': [PARAM, PID, HUMIDITY]})
    humidityPIDPeriod           : u16 = EEPROM.new(default=0,   metadata={'description': _('Periodo de ciclo de inyeccion humedad PID'), 'tags': [PARAM, PID, HUMIDITY]})
    continuousC2H4Threshold     : f32 = EEPROM.new(default=0.0, metadata={'description': _('% error para marcha continua etileno'),      'tags': [PARAM, PID, C2H4]})
    C2H4PIDPeriod               : u16 = EEPROM.new(default=0,   metadata={'description': _('Periodo de ciclo de inyeccion etileno PID'), 'tags': [PARAM, PID, C2H4]})
    outputLimitMaxPIDCO2        : u16 = EEPROM.new(default=0,   metadata={'description': _('Límite superior de salida del PID CO2'),     'tags': [PARAM, PID, CO2]})
    outputLimitMinPIDCO2        : u16 = EEPROM.new(default=0,   metadata={'description': _('Límite inferior de salida del PID CO2'),     'tags': [PARAM, PID, CO2]})
    highLimitSensTempFailure    : u16 = EEPROM.new(default=0,   metadata={'description': _('Límite superior fallo temperatura'),         'tags': [PARAM, ALARM_CFG, TEMPERATURE]})
    lowLimitSensTempFailure     : i16 = EEPROM.new(default=0,   metadata={'description': _('Límite inferior fallo temperatura'),         'tags': [PARAM, ALARM_CFG, TEMPERATURE]})
    lowLimitSensHumidityFailure : u16 = EEPROM.new(default=0,   metadata={'description': _('Límite inferior fallo humedad'),             'tags': [PARAM, ALARM_CFG, HUMIDITY]})
    timerGoOffAlarmTemperatureExt : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer para la repetición valores temperatura exterior'),  'tags': [PARAM, ALARM_CFG, TEMPERATURE]})
    timerGoOffAlarmHumidityExt    : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer para la repetición valores humedadd exterior'),     'tags': [PARAM, ALARM_CFG, HUMIDITY]})
    highLimitSensCO2Failure     : u16 = EEPROM.new(default=0,   metadata={'description': _('Límite superior fallo CO2'),                 'tags': [PARAM, ALARM_CFG, CO2]})
    lowLimitSensCO2Failure      : u16 = EEPROM.new(default=0,   metadata={'description': _('Límite inferior fallo CO2'),                 'tags': [PARAM, ALARM_CFG, CO2]})
    timerGoOffAlarmTemperature  : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer para la repetición valores temperatura'), 'tags': [PARAM, ALARM_CFG, TEMPERATURE]})
    timerGoOffAlarmHumidity     : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer para la repetición valores humedadd'),    'tags': [PARAM, ALARM_CFG, HUMIDITY]})
    timerGoOffAlarmC2H4         : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer para la repetición valores etileno'),     'tags': [PARAM, ALARM_CFG, C2H4]})
    timerGoOffAlarmCO2          : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer para la repetición valores CO2'),         'tags': [PARAM, ALARM_CFG, CO2]})
    timerLimitfAlarmTemperaturePointer : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer alarma de valor fuera de límites de temperatura'), 'tags': [PARAM, ALARM_CFG, TEMPERATURE]})
    timerLimitfAlarmHumidityPointer    : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer alarma de valor fuera de límites de humedad'),     'tags': [PARAM, ALARM_CFG, HUMIDITY]})
    timerLimitfAlarmC2H4Pointer        : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer alarma de valor fuera de límites de etileno'),     'tags': [PARAM, ALARM_CFG, C2H4]})
    timerLimitfAlarmCO2Pointer         : u16 = EEPROM.new(default=0,   metadata={'units': 'sec', 'description': _('Timer alarma de valor fuera de límites de CO2'),         'tags': [PARAM, ALARM_CFG, CO2]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(self.CO2PIDMin)
        encoder.add_16bit_uint(self.CO2PIDMax)
        encoder.add_16bit_uint(self.C2H4PIDMin)
        encoder.add_16bit_uint(self.C2H4PIDMax)
        encoder.add_16bit_uint(self.C2H4FlowPIDMin)
        encoder.add_16bit_uint(self.C2H4FlowPIDMax)
        encoder.add_16bit_uint(self.modbusOffSet)
        encoder.add_16bit_uint(self.chamberVolume)
        encoder.add_16bit_uint(self.extractionHysteresis)
        encoder.add_32bit_uint(self.C2H4GasConcentration) # 32bits
        encoder.add_32bit_float(self.refHumidity)
        encoder.add_32bit_float(self.refTemperature)
        encoder.add_32bit_float(self.refC2H4)
        encoder.add_16bit_uint(self.lowRefCO2)
        encoder.add_16bit_uint(self.highRefCO2)
        encoder.add_32bit_float(self.lowerBandTempStartUpHeat)
        encoder.add_32bit_float(self.upperBandTempStartUpCold)
        encoder.add_32bit_float(self.lowerBandTempStopHeat)
        encoder.add_32bit_float(self.upperBandTempStopCold)
        encoder.add_32bit_float(self.spHighTemperatureAlarm)
        encoder.add_32bit_float(self.spLowTemperatureAlarm)
        encoder.add_32bit_float(self.spHighHumidityAlarm)
        encoder.add_32bit_float(self.spLowHumidityAlarm)
        encoder.add_32bit_float(self.spHighC2H4Alarm)
        encoder.add_32bit_float(self.spLowC2H4Alarm)
        encoder.add_16bit_uint(self.spHighCO2Alarm)

        self.pidHumidity._encode(encoder)
        self.pidCold._encode(encoder)
        self.pidWarm._encode(encoder)
        self.pidCO2._encode(encoder)
        self.pidC2H4._encode(encoder)

        encoder.add_16bit_uint(self.C2H4SensorTime)
        encoder.add_16bit_uint(self.initialInjection)
        encoder.add_16bit_uint(self.intervalInjection)
        encoder.add_16bit_uint(self.durationInjection)
        encoder.add_16bit_uint(self.doorInjection)
        encoder.add_16bit_uint(self.preColdHumidityInjectionTime)
        self.C2H4PressureSensor._encode(encoder)
        encoder.add_32bit_float(self.continuouscCO2Threshold)
        encoder.add_16bit_uint(self.C2H4PressureMin)
        encoder.add_16bit_uint(self.timeNoVentilationAlarm)
        encoder.add_16bit_uint(self.openDoorTimeAlarm1)
        encoder.add_16bit_uint(self.openDoorTimeAlarm2)
        encoder.add_16bit_uint(self.delayTimeStop)

        self.temperatureSensor1._encode(encoder)
        self.humiditySensor1._encode(encoder)
        self.C2H4Sensor1._encode(encoder)
        self.CO2Sensor1._encode(encoder)
        self.temperatureSensor2._encode(encoder)
        self.humiditySensor2._encode(encoder)
        self.C2H4Sensor2._encode(encoder)
        self.CO2Sensor2._encode(encoder)
        self.temperatureOutsideSensor1._encode(encoder)
        self.humidityOutsideSensor1._encode(encoder)
        self.C2H4FlowSensor1._encode(encoder)
        encoder.add_16bit_uint(self.ethylenePressureMin)
        encoder.add_16bit_uint(self.waterPressureMin)
        encoder.add_16bit_uint(self.airPressureMin)
        encoder.add_32bit_float(self.ethyleneValueMin)
        encoder.add_32bit_float(self.ethyleneBarrido)
        encoder.add_16bit_uint(self.timerBarrido)
        self.analogWaterPressureSensor._encode(encoder)
        self.analogAirPressureSensor._encode(encoder)

        encoder.add_32bit_float(self.kFactorW)
        encoder.add_32bit_float(self.kFactorE)
        encoder.add_32bit_float(self.continuousHumidityThreshold)
        encoder.add_16bit_uint(self.humidityPIDPeriod)
        encoder.add_32bit_float(self.continuousC2H4Threshold)
        encoder.add_16bit_uint(self.C2H4PIDPeriod)
        encoder.add_16bit_uint(self.outputLimitMaxPIDCO2)
        encoder.add_16bit_uint(self.outputLimitMinPIDCO2)
        encoder.add_16bit_uint(self.highLimitSensTempFailure)
        encoder.add_16bit_int(self.lowLimitSensTempFailure)
        encoder.add_16bit_uint(self.lowLimitSensHumidityFailure)
        encoder.add_16bit_uint(self.timerGoOffAlarmTemperatureExt)
        encoder.add_16bit_uint(self.timerGoOffAlarmHumidityExt)
        encoder.add_16bit_uint(self.highLimitSensCO2Failure)
        encoder.add_16bit_uint(self.lowLimitSensCO2Failure)
        encoder.add_16bit_uint(self.timerGoOffAlarmTemperature)
        encoder.add_16bit_uint(self.timerGoOffAlarmHumidity)
        encoder.add_16bit_uint(self.timerGoOffAlarmC2H4)
        encoder.add_16bit_uint(self.timerGoOffAlarmCO2)
        encoder.add_16bit_uint(self.timerLimitfAlarmTemperaturePointer)
        encoder.add_16bit_uint(self.timerLimitfAlarmHumidityPointer)
        encoder.add_16bit_uint(self.timerLimitfAlarmC2H4Pointer)
        encoder.add_16bit_uint(self.timerLimitfAlarmCO2Pointer)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.CO2PIDMin                = decoder.decode_16bit_uint()
        self.CO2PIDMax                = decoder.decode_16bit_uint()
        self.C2H4PIDMin               = decoder.decode_16bit_uint()
        self.C2H4PIDMax               = decoder.decode_16bit_uint()
        self.C2H4FlowPIDMin           = decoder.decode_16bit_uint()
        self.C2H4FlowPIDMax           = decoder.decode_16bit_uint()
        self.modbusOffSet             = decoder.decode_16bit_uint()
        self.chamberVolume            = decoder.decode_16bit_uint()
        self.extractionHysteresis     = decoder.decode_16bit_uint()
        self.C2H4GasConcentration     = decoder.decode_32bit_uint() # 32bits
        self.refHumidity              = decoder.decode_32bit_float()
        self.refTemperature           = decoder.decode_32bit_float()
        self.refC2H4                  = decoder.decode_32bit_float()
        self.lowRefCO2                = decoder.decode_16bit_uint()
        self.highRefCO2               = decoder.decode_16bit_uint()
        self.lowerBandTempStartUpHeat = decoder.decode_32bit_float()
        self.upperBandTempStartUpCold = decoder.decode_32bit_float()
        self.lowerBandTempStopHeat    = decoder.decode_32bit_float()
        self.upperBandTempStopCold    = decoder.decode_32bit_float()
        self.spHighTemperatureAlarm   = decoder.decode_32bit_float()
        self.spLowTemperatureAlarm    = decoder.decode_32bit_float()
        self.spHighHumidityAlarm      = decoder.decode_32bit_float()
        self.spLowHumidityAlarm       = decoder.decode_32bit_float()
        self.spHighC2H4Alarm          = decoder.decode_32bit_float()
        self.spLowC2H4Alarm           = decoder.decode_32bit_float()
        self.spHighCO2Alarm           = decoder.decode_16bit_uint()

        self.pidHumidity._decode(decoder)
        self.pidCold._decode(decoder)
        self.pidWarm._decode(decoder)
        self.pidCO2._decode(decoder)
        self.pidC2H4._decode(decoder)

        self.C2H4SensorTime                = decoder.decode_16bit_uint()
        self.initialInjection              = decoder.decode_16bit_uint()
        self.intervalInjection             = decoder.decode_16bit_uint()
        self.durationInjection             = decoder.decode_16bit_uint()
        self.doorInjection                 = decoder.decode_16bit_uint()
        self.preColdHumidityInjectionTime  = decoder.decode_16bit_uint()
        self.C2H4PressureSensor._decode(decoder)
        self.continuouscCO2Threshold       = decoder.decode_32bit_float()
        self.C2H4PressureMin               = decoder.decode_16bit_uint()
        self.timeNoVentilationAlarm        = decoder.decode_16bit_uint()
        self.openDoorTimeAlarm1            = decoder.decode_16bit_uint()
        self.openDoorTimeAlarm2            = decoder.decode_16bit_uint()
        self.delayTimeStop                 = decoder.decode_16bit_uint()

        self.temperatureSensor1._decode(decoder)
        self.humiditySensor1._decode(decoder)
        self.C2H4Sensor1._decode(decoder)
        self.CO2Sensor1._decode(decoder)
        self.temperatureSensor2._decode(decoder)
        self.humiditySensor2._decode(decoder)
        self.C2H4Sensor2._decode(decoder)
        self.CO2Sensor2._decode(decoder)
        self.temperatureOutsideSensor1._decode(decoder)
        self.humidityOutsideSensor1._decode(decoder)
        self.C2H4FlowSensor1._decode(decoder)
        self.ethylenePressureMin = decoder.decode_16bit_uint()
        self.waterPressureMin    = decoder.decode_16bit_uint()
        self.airPressureMin      = decoder.decode_16bit_uint()
        self.ethyleneValueMin    = decoder.decode_32bit_float()
        self.ethyleneBarrido     = decoder.decode_32bit_float()
        self.timerBarrido        = decoder.decode_16bit_uint()
        self.analogWaterPressureSensor._decode(decoder)
        self.analogAirPressureSensor._decode(decoder)

        self.kFactorW                            = decoder.decode_16bit_uint()
        self.kFactorE                            = decoder.decode_16bit_uint()
        self.continuousHumidityThreshold         = decoder.decode_32bit_float()
        self.humidityPIDPeriod                   = decoder.decode_16bit_uint()
        self.continuousC2H4Threshold             = decoder.decode_32bit_float()
        self.C2H4PIDPeriod                       = decoder.decode_16bit_uint()
        self.outputLimitMaxPIDCO2                = decoder.decode_16bit_uint()
        self.outputLimitMinPIDCO2                = decoder.decode_16bit_uint()
        self.highLimitSensTempFailure            = decoder.decode_16bit_uint()
        self.lowLimitSensTempFailure             = decoder.decode_16bit_int()
        self.lowLimitSensHumidityFailure         = decoder.decode_16bit_uint()
        self.timerGoOffAlarmTemperatureExt       = decoder.decode_16bit_uint()
        self.timerGoOffAlarmHumidityExt          = decoder.decode_16bit_uint()
        self.highLimitSensCO2Failure             = decoder.decode_16bit_uint()
        self.lowLimitSensCO2Failure              = decoder.decode_16bit_uint()
        self.timerGoOffAlarmTemperature          = decoder.decode_16bit_uint()
        self.timerGoOffAlarmHumidity             = decoder.decode_16bit_uint()
        self.timerGoOffAlarmC2H4                 = decoder.decode_16bit_uint()
        self.timerGoOffAlarmCO2                  = decoder.decode_16bit_uint()
        self.timerLimitfAlarmTemperaturePointer  = decoder.decode_16bit_uint()
        self.timerLimitfAlarmHumidityPointer     = decoder.decode_16bit_uint()
        self.timerLimitfAlarmC2H4Pointer         = decoder.decode_16bit_uint()
        self.timerLimitfAlarmCO2Pointer          = decoder.decode_16bit_uint()


@dataclass
class Block04(MBusSerializable):
    enableAlarmSet               : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado alarma'),                  'tags': [PARAM, BASIC, ENABLED]})
    enableEvaporatorFanActivator : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador evaporizador'), 'tags': [PARAM, BASIC, ENABLED]})
    enableAeroheaters            : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado Aerotermos'),              'tags': [PARAM, BASIC, ENABLED]})
    enableHumidityWatersValves   : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado Humedad'),                 'tags': [PARAM, BASIC, ENABLED]})
    enableEthylene               : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado Etileno'),                 'tags': [PARAM, BASIC, ENABLED]})
    enableFanIn1                 : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador entrada 1'),    'tags': [PARAM, BASIC, ENABLED]})
    enableFanOut1                : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador salida 1'),     'tags': [PARAM, BASIC, ENABLED]})
    enableFanIn2                 : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador entrada 2'),    'tags': [PARAM, BASIC, ENABLED]})
    enableFanOut2                : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador salida 2'),     'tags': [PARAM, BASIC, ENABLED]})
    enableCoolingRequest         : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado pedido de frío'),          'tags': [PARAM, BASIC, ENABLED]})
    enableHeatingRequest         : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado pedido de calor'),         'tags': [PARAM, BASIC, ENABLED]})
    enableControlCoolingRequest  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado pedido control de frío'),  'tags': [PARAM, BASIC, ENABLED]})
    enableControlHeatingRequest  : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado pedido control calor'),    'tags': [PARAM, BASIC, ENABLED]})
    enableSafetyRelayReset       : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado del rele de rearme'),      'tags': [PARAM, BASIC, ENABLED]})
    enableHumidityAirValves      : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado boquilla aire'),           'tags': [PARAM, BASIC, ENABLED]})
    _reserved_04_15              : bool = EEPROM.new(default=False, metadata={'description': _('Reserved bit 15'),                    'tags': [RESERVED]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.enableAlarmSet,
            self.enableEvaporatorFanActivator,
            self.enableAeroheaters,
            self.enableHumidityWatersValves,
            self.enableEthylene,
            self.enableFanIn1,
            self.enableFanOut1,
            self.enableFanIn2,
            self.enableFanOut2,
            self.enableCoolingRequest,
            self.enableHeatingRequest,
            self.enableControlCoolingRequest,
            self.enableControlHeatingRequest,
            self.enableSafetyRelayReset,
            self.enableHumidityAirValves,
            False, # self._reserved_04_15,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.enableAlarmSet               = flags[0]
        self.enableEvaporatorFanActivator = flags[1]
        self.enableAeroheaters            = flags[2]
        self.enableHumidityWatersValves   = flags[3]
        self.enableEthylene               = flags[4]
        self.enableFanIn1                 = flags[5]
        self.enableFanOut1                = flags[6]
        self.enableFanIn2                 = flags[7]
        self.enableFanOut2                = flags[8]
        self.enableCoolingRequest         = flags[9]
        self.enableHeatingRequest         = flags[10]
        self.enableControlCoolingRequest  = flags[11]
        self.enableControlHeatingRequest  = flags[12]
        self.enableSafetyRelayReset       = flags[13]
        self.enableHumidityAirValves      = flags[14]
        # self._reserved_04_15              = flags[15]

@dataclass
class Block05(MBusSerializable):
    pidC2H4Flow  : PIDControllerParams = field(default_factory=lambda: PIDControllerParams(), metadata={'description': _('Constantes regulador PID caudal C2H4'), 'tags': [PARAM, PID, C2H4]})
    highLimitSensC2H4Failure       : f32 = EEPROM.new(default=0.0, metadata={'description': _('Límite superior fallo etileno'),              'tags': [PARAM, ALARM_CFG, C2H4]})
    lowLimitSensC2H4Failure        : f32 = EEPROM.new(default=0.0, metadata={'description': _('Límite inferior fallo etileno'),              'tags': [PARAM, ALARM_CFG, C2H4]})
    highLimitSensTempExtFailure    : u16 = EEPROM.new(default=0,   metadata={'description': _('Límite superior fallo temperatura exterior'), 'tags': [PARAM, ALARM_CFG, TEMPERATURE]})
    lowLimitSensTempExtFailure     : i16 = EEPROM.new(default=0,   metadata={'description': _('Límite inferior fallo temperatura exterior'), 'tags': [PARAM, ALARM_CFG, TEMPERATURE]})
    lowLimitSensHumidityExtFailure : i16 = EEPROM.new(default=0,   metadata={'description': _('Límite inferior fallo humedad exterior'),     'tags': [PARAM, ALARM_CFG, HUMIDITY]})
    timerC2H4Fail                  : f32 = EEPROM.new(default=0.0, metadata={'description': _('Timer fallo etileno'),                        'tags': [PARAM, ALARM_CFG, C2H4]})

    _reserved173 : u16 = MemMapped.new(default=0, metadata={'description': _('Reserved base+173'), 'tags': [RESERVED]})
    _reserved174 : u16 = MemMapped.new(default=0, metadata={'description': _('Reserved base+174'), 'tags': [RESERVED]})
    _reserved175 : u16 = MemMapped.new(default=0, metadata={'description': _('Reserved base+175'), 'tags': [RESERVED]})
    _reserved176 : u16 = MemMapped.new(default=0, metadata={'description': _('Reserved base+176'), 'tags': [RESERVED]})
    _reserved177 : u16 = MemMapped.new(default=0, metadata={'description': _('Reserved base+177'), 'tags': [RESERVED]})
    _reserved178 : u16 = MemMapped.new(default=0, metadata={'description': _('Reserved base+178'), 'tags': [RESERVED]})

    airHeater1PhaseSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater1PhaseSensor'),   'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater2PhaseSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater2PhaseSensor'),   'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater3PhaseSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater3PhaseSensor'),   'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater4PhaseSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater4PhaseSensor'),   'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater5PhaseSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater5PhaseSensor'),   'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater6PhaseSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater6PhaseSensor'),   'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater7PhaseSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater7PhaseSensor'),   'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater8PhaseSensor   : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater8PhaseSensor'),   'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater1NeutralSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater1NeutralSensor'), 'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater2NeutralSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater2NeutralSensor'), 'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater3NeutralSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater3NeutralSensor'), 'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater4NeutralSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater4NeutralSensor'), 'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater5NeutralSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater5NeutralSensor'), 'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater6NeutralSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater6NeutralSensor'), 'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater7NeutralSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater7NeutralSensor'), 'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    airHeater8NeutralSensor : SensorParams = field(default_factory=lambda: SensorParams(units='--'), metadata={'description': _('Configuración sensor airHeater8NeutralSensor'), 'tags': [PARAM, SENSOR, AIR_HEATER, TEMPERATURE]})
    timeOnFan               : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo encendido ventilador'),   'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    timeoOffFan             : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo apagado ventilador'),     'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    timeOnResistor          : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo encendido resistencia'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    timeOffResistor         : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo apagado resistencia'),    'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    timeResistorFan         : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo resistencia ventilador'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    timeNeutralCurrent      : u16 = EEPROM.new(default=0, metadata={'units': 'sec', 'description': _('Tiempo alarma fase'),            'tags': [PARAM, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        self.pidC2H4Flow._encode(encoder)
        encoder.add_32bit_float(self.highLimitSensC2H4Failure)
        encoder.add_32bit_float(self.lowLimitSensC2H4Failure)
        encoder.add_16bit_uint(self.highLimitSensTempExtFailure)
        encoder.add_16bit_int(self.lowLimitSensTempExtFailure)
        encoder.add_16bit_int(self.lowLimitSensHumidityExtFailure)
        encoder.add_32bit_float(self.timerC2H4Fail)

        encoder.add_16bit_uint(self._reserved173)
        encoder.add_16bit_uint(self._reserved174)
        encoder.add_16bit_uint(self._reserved175)
        encoder.add_16bit_uint(self._reserved176)
        encoder.add_16bit_uint(self._reserved177)
        encoder.add_16bit_uint(self._reserved178)

        self.airHeater1PhaseSensor._encode(encoder)
        self.airHeater2PhaseSensor._encode(encoder)
        self.airHeater3PhaseSensor._encode(encoder)
        self.airHeater4PhaseSensor._encode(encoder)
        self.airHeater5PhaseSensor._encode(encoder)
        self.airHeater6PhaseSensor._encode(encoder)
        self.airHeater7PhaseSensor._encode(encoder)
        self.airHeater8PhaseSensor._encode(encoder)
        self.airHeater1NeutralSensor._encode(encoder)
        self.airHeater2NeutralSensor._encode(encoder)
        self.airHeater3NeutralSensor._encode(encoder)
        self.airHeater4NeutralSensor._encode(encoder)
        self.airHeater5NeutralSensor._encode(encoder)
        self.airHeater6NeutralSensor._encode(encoder)
        self.airHeater7NeutralSensor._encode(encoder)
        self.airHeater8NeutralSensor._encode(encoder)

        encoder.add_16bit_uint(self.timeOnFan)
        encoder.add_16bit_uint(self.timeoOffFan)
        encoder.add_16bit_uint(self.timeOnResistor)
        encoder.add_16bit_uint(self.timeOffResistor)
        encoder.add_16bit_uint(self.timeResistorFan)
        encoder.add_16bit_uint(self.timeNeutralCurrent)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.pidC2H4Flow._decode(decoder)
        self.highLimitSensC2H4Failure            = decoder.decode_32bit_float()
        self.lowLimitSensC2H4Failure             = decoder.decode_32bit_float()
        self.highLimitSensTempExtFailure         = decoder.decode_16bit_uint()
        self.lowLimitSensTempExtFailure          = decoder.decode_16bit_int()
        self.lowLimitSensHumidityExtFailure      = decoder.decode_16bit_int()
        self.timerC2H4Fail                       = decoder.decode_32bit_float()

        self._reserved173 = decoder.decode_16bit_uint()
        self._reserved174 = decoder.decode_16bit_uint()
        self._reserved175 = decoder.decode_16bit_uint()
        self._reserved176 = decoder.decode_16bit_uint()
        self._reserved177 = decoder.decode_16bit_uint()
        self._reserved178 = decoder.decode_16bit_uint()

        self.airHeater1PhaseSensor._decode(decoder)
        self.airHeater2PhaseSensor._decode(decoder)
        self.airHeater3PhaseSensor._decode(decoder)
        self.airHeater4PhaseSensor._decode(decoder)
        self.airHeater5PhaseSensor._decode(decoder)
        self.airHeater6PhaseSensor._decode(decoder)
        self.airHeater7PhaseSensor._decode(decoder)
        self.airHeater8PhaseSensor._decode(decoder)
        self.airHeater1NeutralSensor._decode(decoder)
        self.airHeater2NeutralSensor._decode(decoder)
        self.airHeater3NeutralSensor._decode(decoder)
        self.airHeater4NeutralSensor._decode(decoder)
        self.airHeater5NeutralSensor._decode(decoder)
        self.airHeater6NeutralSensor._decode(decoder)
        self.airHeater7NeutralSensor._decode(decoder)
        self.airHeater8NeutralSensor._decode(decoder)

        self.timeOnFan          = decoder.decode_16bit_uint()
        self.timeoOffFan        = decoder.decode_16bit_uint()
        self.timeOnResistor     = decoder.decode_16bit_uint()
        self.timeOffResistor    = decoder.decode_16bit_uint()
        self.timeResistorFan    = decoder.decode_16bit_uint()
        self.timeNeutralCurrent = decoder.decode_16bit_uint()

@dataclass
class Block06(MBusSerializable):
    fanOn1          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador aerotermo 1'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    fanOn2          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador aerotermo 2'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    fanOn3          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador aerotermo 3'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    fanOn4          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador aerotermo 4'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    fanOn5          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador aerotermo 5'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    fanOn6          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador aerotermo 6'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    fanOn7          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador aerotermo 7'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    fanOn8          : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado ventilador aerotermo 8'),  'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    resistorOn1     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado resistencia aerotermo 1'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    resistorOn2     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado resistencia aerotermo 2'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    resistorOn3     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado resistencia aerotermo 3'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    resistorOn4     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado resistencia aerotermo 4'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    resistorOn5     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado resistencia aerotermo 5'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    resistorOn6     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado resistencia aerotermo 6'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    resistorOn7     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado resistencia aerotermo 7'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})
    resistorOn8     : bool = EEPROM.new(default=False, metadata={'description': _('Habilitado resistencia aerotermo 8'), 'tags': [PARAM, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.fanOn1,
            self.fanOn2,
            self.fanOn3,
            self.fanOn4,
            self.fanOn5,
            self.fanOn6,
            self.fanOn7,
            self.fanOn8,
            self.resistorOn1,
            self.resistorOn2,
            self.resistorOn3,
            self.resistorOn4,
            self.resistorOn5,
            self.resistorOn6,
            self.resistorOn7,
            self.resistorOn8,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.fanOn1      = flags[0]
        self.fanOn2      = flags[1]
        self.fanOn3      = flags[2]
        self.fanOn4      = flags[3]
        self.fanOn5      = flags[4]
        self.fanOn6      = flags[5]
        self.fanOn7      = flags[6]
        self.fanOn8      = flags[7]
        self.resistorOn1 = flags[8]
        self.resistorOn2 = flags[9]
        self.resistorOn3 = flags[10]
        self.resistorOn4 = flags[11]
        self.resistorOn5 = flags[12]
        self.resistorOn6 = flags[13]
        self.resistorOn7 = flags[14]
        self.resistorOn8 = flags[15]

@dataclass
class Block07(MBusSerializable):
    emergencyStop        : bool = MemMapped.new(default=False, metadata={'description': _('Seta de emergencia'),        'tags': [IODATA, SYSTEM]})
    safetyRelayReset     : bool = MemMapped.new(default=False, metadata={'description': _('Rearme relé seguridad'),     'tags': [IODATA, SYSTEM]})
    evaporatorFanOn      : bool = MemMapped.new(default=False, metadata={'description': _('Puesta en marcha ventiladores evaporadores'),   'tags': [IODATA, C2H4]})
    _reserved_07_03      : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 03'), 'tags': [RESERVED]})
    start1               : bool = MemMapped.new(default=False, metadata={'description': _('Inicio ciclo de inyección inicial de etileno'), 'tags': [IODATA, C2H4, GAS_BALANCE]})
    initialInjectionC2H4 : bool = MemMapped.new(default=False, metadata={'description': _('Fin de inyeccion inicial de etileno'),          'tags': [IODATA, C2H4, GAS_BALANCE]}) #  mensaje: verificar inyeccion inicial etileno e iniciar ciclo.
    photocell1           : bool = MemMapped.new(default=False, metadata={'description': _('Fotocélula 1'),                                 'tags': [IODATA, C2H4, GAS_BALANCE]})
    photocell2           : bool = MemMapped.new(default=False, metadata={'description': _('Fotocélula 2'),                                 'tags': [IODATA, C2H4, GAS_BALANCE]})
    fridgeControlRequest : bool = MemMapped.new(default=False, metadata={'description': _('Petición control de frío'),                          'tags': [IODATA, TEMPERATURE]})
    heaterControlRequest : bool = MemMapped.new(default=False, metadata={'description': _('Petición control de calor'),                         'tags': [IODATA, TEMPERATURE]})
    fridgeAvailable      : bool = MemMapped.new(default=False, metadata={'description': _('Confirmación equipo climatización preparado frío'),  'tags': [IODATA, TEMPERATURE]})
    heaterAvailable      : bool = MemMapped.new(default=False, metadata={'description': _('Confirmación equipo climatización preparado calor'), 'tags': [IODATA, TEMPERATURE]})
    fridgeRequest        : bool = MemMapped.new(default=False, metadata={'description': _('Petición de frío'),                                  'tags': [IODATA, TEMPERATURE]})
    heaterRequest        : bool = MemMapped.new(default=False, metadata={'description': _('Petición calor'),                                    'tags': [IODATA, TEMPERATURE]})
    fridgeOn             : bool = MemMapped.new(default=False, metadata={'description': _('Frío activado'),                                     'tags': [IODATA, TEMPERATURE]})
    heaterOn             : bool = MemMapped.new(default=False, metadata={'description': _('Calor activado'),                                    'tags': [IODATA, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.emergencyStop,
            self.safetyRelayReset,
            self.evaporatorFanOn,
            False, # self._reserved_07_03
            self.start1,
            self.initialInjectionC2H4,
            self.photocell1,
            self.photocell2,
            self.fridgeControlRequest,
            self.heaterControlRequest,
            self.fridgeAvailable,
            self.heaterAvailable,
            self.fridgeRequest,
            self.heaterRequest,
            self.fridgeOn,
            self.heaterOn,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.emergencyStop        = flags[0]
        self.safetyRelayReset     = flags[1]
        self.evaporatorFanOn      = flags[2]
        self._reserved_07_03      = flags[3]
        self.start1               = flags[4]
        self.initialInjectionC2H4 = flags[5]
        self.photocell1           = flags[6]
        self.photocell2           = flags[7]
        self.fridgeControlRequest = flags[8]
        self.heaterControlRequest = flags[9]
        self.fridgeAvailable      = flags[10]
        self.heaterAvailable      = flags[11]
        self.fridgeRequest        = flags[12]
        self.heaterRequest        = flags[13]
        self.fridgeOn             = flags[14]
        self.heaterOn             = flags[15]

@dataclass
class Block08(MBusSerializable):
    defrostCycle       : bool = MemMapped.new(default=False, metadata={'description': _('Ciclo de desescarche'),             'tags': [IODATA, TEMPERATURE]})
    electrovalveWater1 : bool = MemMapped.new(default=False, metadata={'description': _('Activación electroválvula agua 1'), 'tags': [IODATA, HUMIDITY]})
    electrovalveWater2 : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula agua 2'), 'tags': [IODATA, HUMIDITY]})
    electrovalveWater3 : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula agua 3'), 'tags': [IODATA, HUMIDITY]})
    electrovalveWater4 : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula agua 4'), 'tags': [IODATA, HUMIDITY]})
    electrovalveWater5 : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula agua 5'), 'tags': [IODATA, HUMIDITY]})
    electrovalveWater6 : bool = MemMapped.new(default=False, metadata={'description': _('Activación electroválvula agua 6'), 'tags': [IODATA, HUMIDITY]})
    electrovalveWater7 : bool = MemMapped.new(default=False, metadata={'description': _('Activación electroválvula agua 7'), 'tags': [IODATA, HUMIDITY]})
    electrovalveWater8 : bool = MemMapped.new(default=False, metadata={'description': _('Activación electroválvula agua 8'), 'tags': [IODATA, HUMIDITY]})
    electrovalveAir1   : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula aire 1'), 'tags': [IODATA, HUMIDITY]})
    electrovalveAir2   : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula aire 2'), 'tags': [IODATA, HUMIDITY]})
    electrovalveAir3   : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula aire 3'), 'tags': [IODATA, HUMIDITY]})
    electrovalveAir4   : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula aire 4'), 'tags': [IODATA, HUMIDITY]})
    electrovalveAir5   : bool = MemMapped.new(default=False, metadata={'description': _('Activación Electroválvula aire 5'), 'tags': [IODATA, HUMIDITY]})
    electrovalveAir6   : bool = MemMapped.new(default=False, metadata={'description': _('Activación electroválvula aire 6'), 'tags': [IODATA, HUMIDITY]})
    electrovalveAir7   : bool = MemMapped.new(default=False, metadata={'description': _('Activación electroválvula aire 7'), 'tags': [IODATA, HUMIDITY]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.defrostCycle,
            self.electrovalveWater1,
            self.electrovalveWater2,
            self.electrovalveWater3,
            self.electrovalveWater4,
            self.electrovalveWater5,
            self.electrovalveWater6,
            self.electrovalveWater7,
            self.electrovalveWater8,
            self.electrovalveAir1,
            self.electrovalveAir2,
            self.electrovalveAir3,
            self.electrovalveAir4,
            self.electrovalveAir5,
            self.electrovalveAir6,
            self.electrovalveAir7,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.defrostCycle       = flags[0]
        self.electrovalveWater1 = flags[1]
        self.electrovalveWater2 = flags[2]
        self.electrovalveWater3 = flags[3]
        self.electrovalveWater4 = flags[4]
        self.electrovalveWater5 = flags[5]
        self.electrovalveWater6 = flags[6]
        self.electrovalveWater7 = flags[7]
        self.electrovalveWater8 = flags[8]
        self.electrovalveAir1   = flags[9]
        self.electrovalveAir2   = flags[10]
        self.electrovalveAir3   = flags[11]
        self.electrovalveAir4   = flags[12]
        self.electrovalveAir5   = flags[13]
        self.electrovalveAir6   = flags[14]
        self.electrovalveAir7   = flags[15]

@dataclass
class Block09(MBusSerializable):
    electrovalveAir8       : bool = MemMapped.new(default=False, metadata={'description': _('Activación electroválvula aire 8'),     'tags': [IODATA, HUMIDITY]})
    humiditySystem1        : bool = MemMapped.new(default=False, metadata={'description': _('Activación equipo humedad 1'),          'tags': [IODATA, HUMIDITY]})
    humiditySystem2        : bool = MemMapped.new(default=False, metadata={'description': _('Activación equipo humedad 2'),          'tags': [IODATA, HUMIDITY]})
    humiditySystem3        : bool = MemMapped.new(default=False, metadata={'description': _('Activación equipo humedad 3'),          'tags': [IODATA, HUMIDITY]})
    humiditySystem4        : bool = MemMapped.new(default=False, metadata={'description': _('Activación equipo humedad 4'),          'tags': [IODATA, HUMIDITY]})
    humiditySystem5        : bool = MemMapped.new(default=False, metadata={'description': _('Activación equipo humedad 5'),          'tags': [IODATA, HUMIDITY]})
    humiditySystem6        : bool = MemMapped.new(default=False, metadata={'description': _('Activación equipo humedad 6'),          'tags': [IODATA, HUMIDITY]})
    C2H4Valve              : bool = MemMapped.new(default=False, metadata={'description': _('Activación electroválvula de etileno'), 'tags': [IODATA, C2H4]})
    airElectrovalveForced1 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula aire 1'),        'tags': [IODATA, FORCED, HUMIDITY]})
    airElectrovalveForced2 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula aire 2'),        'tags': [IODATA, FORCED, HUMIDITY]})
    airElectrovalveForced3 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula aire 3'),        'tags': [IODATA, FORCED, HUMIDITY]})
    airElectrovalveForced4 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula aire 4'),        'tags': [IODATA, FORCED, HUMIDITY]})
    airElectrovalveForced5 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula aire 5'),        'tags': [IODATA, FORCED, HUMIDITY]})
    airElectrovalveForced6 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula aire 6'),        'tags': [IODATA, FORCED, HUMIDITY]})
    airElectrovalveForced7 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula aire 7'),        'tags': [IODATA, FORCED, HUMIDITY]})
    airElectrovalveForced8 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula aire 8'),        'tags': [IODATA, FORCED, HUMIDITY]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.electrovalveAir8,
            self.humiditySystem1,
            self.humiditySystem2,
            self.humiditySystem3,
            self.humiditySystem4,
            self.humiditySystem5,
            self.humiditySystem6,
            self.C2H4Valve,
            self.airElectrovalveForced1,
            self.airElectrovalveForced2,
            self.airElectrovalveForced3,
            self.airElectrovalveForced4,
            self.airElectrovalveForced5,
            self.airElectrovalveForced6,
            self.airElectrovalveForced7,
            self.airElectrovalveForced8,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.electrovalveAir8       = flags[0]
        self.humiditySystem1        = flags[1]
        self.humiditySystem2        = flags[2]
        self.humiditySystem3        = flags[3]
        self.humiditySystem4        = flags[4]
        self.humiditySystem5        = flags[5]
        self.humiditySystem6        = flags[6]
        self.C2H4Valve              = flags[7]
        self.airElectrovalveForced1 = flags[8]
        self.airElectrovalveForced2 = flags[9]
        self.airElectrovalveForced3 = flags[10]
        self.airElectrovalveForced4 = flags[11]
        self.airElectrovalveForced5 = flags[12]
        self.airElectrovalveForced6 = flags[13]
        self.airElectrovalveForced7 = flags[14]
        self.airElectrovalveForced8 = flags[15]

@dataclass
class Block10(MBusSerializable):
    waterElectrovalveForced1 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula agua 1'),    'tags': [IODATA, FORCED, HUMIDITY]})
    waterElectrovalveForced2 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula agua 2'),    'tags': [IODATA, FORCED, HUMIDITY]})
    waterElectrovalveForced3 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula agua 3'),    'tags': [IODATA, FORCED, HUMIDITY]})
    waterElectrovalveForced4 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula agua 4'),    'tags': [IODATA, FORCED, HUMIDITY]})
    waterElectrovalveForced5 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula agua 5'),    'tags': [IODATA, FORCED, HUMIDITY]})
    waterElectrovalveForced6 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula agua 6'),    'tags': [IODATA, FORCED, HUMIDITY]})
    waterElectrovalveForced7 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula agua 7'),    'tags': [IODATA, FORCED, HUMIDITY]})
    waterElectrovalveForced8 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula agua 8'),    'tags': [IODATA, FORCED, HUMIDITY]})
    C2H4Electrovalve1        : bool = MemMapped.new(default=False, metadata={'description': _('Forzado electroválvula etileno 1'), 'tags': [IODATA, FORCED, C2H4]})
    inFanForced1             : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador entrada 1'),     'tags': [IODATA, FORCED, CO2]})
    outFanForced1            : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador salida 1'),      'tags': [IODATA, FORCED, CO2]})
    inFanForced2             : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador entrada 2'),     'tags': [IODATA, FORCED, CO2]})
    outFanForced2            : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador salida 2'),      'tags': [IODATA, FORCED, CO2]})
    highTemperatureAlarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma alta temperatura'),          'tags': [ALARM, TEMPERATURE]})
    lowTemperatureAlarm      : bool = MemMapped.new(default=False, metadata={'description': _('Alarma baja temperatura'),          'tags': [ALARM, TEMPERATURE]})
    highHumidityAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma alta humedad'),              'tags': [ALARM, HUMIDITY]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.waterElectrovalveForced1,
            self.waterElectrovalveForced2,
            self.waterElectrovalveForced3,
            self.waterElectrovalveForced4,
            self.waterElectrovalveForced5,
            self.waterElectrovalveForced6,
            self.waterElectrovalveForced7,
            self.waterElectrovalveForced8,
            self.C2H4Electrovalve1,
            self.inFanForced1,
            self.outFanForced1,
            self.inFanForced2,
            self.outFanForced2,
            self.highTemperatureAlarm,
            self.lowTemperatureAlarm,
            self.highHumidityAlarm,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.waterElectrovalveForced1 = flags[0]
        self.waterElectrovalveForced2 = flags[1]
        self.waterElectrovalveForced3 = flags[2]
        self.waterElectrovalveForced4 = flags[3]
        self.waterElectrovalveForced5 = flags[4]
        self.waterElectrovalveForced6 = flags[5]
        self.waterElectrovalveForced7 = flags[6]
        self.waterElectrovalveForced8 = flags[7]
        self.C2H4Electrovalve1        = flags[8]
        self.inFanForced1             = flags[9]
        self.outFanForced1            = flags[10]
        self.inFanForced2             = flags[11]
        self.outFanForced2            = flags[12]
        self.highTemperatureAlarm     = flags[13]
        self.lowTemperatureAlarm      = flags[14]
        self.highHumidityAlarm        = flags[15]

@dataclass
class Block11(MBusSerializable):
    lowHumidityAlarm         : bool = MemMapped.new(default=False, metadata={'description': _('Alarma baja humedad'),                             'tags': [ALARM, HUMIDITY]})
    highC2H4Alarm            : bool = MemMapped.new(default=False, metadata={'description': _('Alarma alto etileno'),                             'tags': [ALARM, C2H4]})
    lowC2H4Alarm             : bool = MemMapped.new(default=False, metadata={'description': _('Alarma bajo etileno'),                             'tags': [ALARM, C2H4]})
    highCO2Alarm             : bool = MemMapped.new(default=False, metadata={'description': _('Alarma alto CO2'),                                 'tags': [ALARM, CO2]})
    tempSenFailure1Alarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor de temperatura 1'),      'tags': [ALARM, TEMPERATURE]})
    tempSenFailure2Alarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor de temperatura 2'),      'tags': [ALARM, TEMPERATURE]})
    humiditySenFailure1Alarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor de humedad 1'),          'tags': [ALARM, HUMIDITY]})
    humiditySenFailure2Alarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor de humedad 2'),          'tags': [ALARM, HUMIDITY]})
    C2H4SenFailure1Alarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor de Etileno 1'),          'tags': [ALARM, C2H4]})
    C2H4SenFailure2Alarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor de Etileno 2'),          'tags': [ALARM, C2H4]})
    CO2SenFailure1Alarm      : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor de CO2 1'),              'tags': [ALARM, CO2]})
    CO2SenFailure2Alarm      : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor de CO2 2'),              'tags': [ALARM, CO2]})
    tempSenBlocked1Alarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de temperatura 1'), 'tags': [ALARM, TEMPERATURE]})
    tempSenBlocked2Alarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de temperatura 2'), 'tags': [ALARM, TEMPERATURE]})
    humiditySenBlocked1Alarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de humedad 1'),     'tags': [ALARM, HUMIDITY]})
    humiditySenBlocked2Alarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de humedad 2'),     'tags': [ALARM, HUMIDITY]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.lowHumidityAlarm,
            self.highC2H4Alarm,
            self.lowC2H4Alarm,
            self.highCO2Alarm,
            self.tempSenFailure1Alarm,
            self.tempSenFailure2Alarm,
            self.humiditySenFailure1Alarm,
            self.humiditySenFailure2Alarm,
            self.C2H4SenFailure1Alarm,
            self.C2H4SenFailure2Alarm,
            self.CO2SenFailure1Alarm,
            self.CO2SenFailure2Alarm,
            self.tempSenBlocked1Alarm,
            self.tempSenBlocked2Alarm,
            self.humiditySenBlocked1Alarm,
            self.humiditySenBlocked2Alarm,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.lowHumidityAlarm         = flags[0]
        self.highC2H4Alarm            = flags[1]
        self.lowC2H4Alarm             = flags[2]
        self.highCO2Alarm             = flags[3]
        self.tempSenFailure1Alarm     = flags[4]
        self.tempSenFailure2Alarm     = flags[5]
        self.humiditySenFailure1Alarm = flags[6]
        self.humiditySenFailure2Alarm = flags[7]
        self.C2H4SenFailure1Alarm     = flags[8]
        self.C2H4SenFailure2Alarm     = flags[9]
        self.CO2SenFailure1Alarm      = flags[10]
        self.CO2SenFailure2Alarm      = flags[11]
        self.tempSenBlocked1Alarm     = flags[12]
        self.tempSenBlocked2Alarm     = flags[13]
        self.humiditySenBlocked1Alarm = flags[14]
        self.humiditySenBlocked2Alarm = flags[15]

@dataclass
class Block12(MBusSerializable):
    C2H4SenBlocked1Alarm   : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de Etileno 1'), 'tags': [ALARM, C2H4]})
    C2H4SenBlocked2Alarm   : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de Etileno 2'), 'tags': [ALARM, C2H4]})
    CO2SenBlocked1Alarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de CO2 1'),     'tags': [ALARM, CO2]})
    CO2SenBlocked2Alarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de CO2 2'),     'tags': [ALARM, CO2]})
    waterLowPressureAlarm  : bool = MemMapped.new(default=False, metadata={'description': _('Alarma baja presión de agua'),                 'tags': [ALARM, HUMIDITY]})
    airLowPressureAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma baja presión de aire'),                 'tags': [ALARM, HUMIDITY]})
    C2H4SensorDelayAlarm   : bool = MemMapped.new(default=False, metadata={'description': _('Alarma tiempo reacción sensor etileno'),       'tags': [ALARM, C2H4]})
    openDoorAlarm1         : bool = MemMapped.new(default=False, metadata={'description': _('Alarma exceso tiempo puerta abierta 1'),       'tags': [ALARM, CO2]})
    openDoorAlarm2         : bool = MemMapped.new(default=False, metadata={'description': _('Alarma exceso tiempo puerta abierta 2'),       'tags': [ALARM, CO2]})
    inFan1NeutralAlarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma neutro ventilador de entrada 1'),       'tags': [ALARM, CO2]})
    outFan1NeutralAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma neutro ventilador de salida 1'),        'tags': [ALARM, CO2]})
    inFan2NeutralAlarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma neutro ventilador de entrada 2'),       'tags': [ALARM, CO2]})
    outFan2NeutralAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma neutro ventilador de salida 2'),        'tags': [ALARM, CO2]})
    inFanClixon1Alarm      : bool = MemMapped.new(default=False, metadata={'description': _('Alarma Clixon ventilador de entrada 1'),       'tags': [ALARM, CO2]})
    outFanClixon1Alarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma Clixon ventilador de salida 1'),        'tags': [ALARM, CO2]})
    inFanClixon2Alarm      : bool = MemMapped.new(default=False, metadata={'description': _('Alarma Clixon ventilador de entrada 2'),       'tags': [ALARM, CO2]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.C2H4SenBlocked1Alarm,
            self.C2H4SenBlocked2Alarm,
            self.CO2SenBlocked1Alarm,
            self.CO2SenBlocked2Alarm,
            self.waterLowPressureAlarm,
            self.airLowPressureAlarm,
            self.C2H4SensorDelayAlarm,
            self.openDoorAlarm1,
            self.openDoorAlarm2,
            self.inFan1NeutralAlarm,
            self.outFan1NeutralAlarm,
            self.inFan2NeutralAlarm,
            self.outFan2NeutralAlarm,
            self.inFanClixon1Alarm,
            self.outFanClixon1Alarm,
            self.inFanClixon2Alarm,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.C2H4SenBlocked1Alarm  = flags[0]
        self.C2H4SenBlocked2Alarm  = flags[1]
        self.CO2SenBlocked1Alarm   = flags[2]
        self.CO2SenBlocked2Alarm   = flags[3]
        self.waterLowPressureAlarm = flags[4]
        self.airLowPressureAlarm   = flags[5]
        self.C2H4SensorDelayAlarm  = flags[6]
        self.openDoorAlarm1        = flags[7]
        self.openDoorAlarm2        = flags[8]
        self.inFan1NeutralAlarm    = flags[9]
        self.outFan1NeutralAlarm   = flags[10]
        self.inFan2NeutralAlarm    = flags[11]
        self.outFan2NeutralAlarm   = flags[12]
        self.inFanClixon1Alarm     = flags[13]
        self.outFanClixon1Alarm    = flags[14]
        self.inFanClixon2Alarm     = flags[15]

@dataclass
class Block13(MBusSerializable):
    outFanClixon2Alarm      : bool = MemMapped.new(default=False, metadata={'description': _('AlarmaClixon ventilador de salida2'),   'tags': [ALARM, CO2]})
    inFanTerm1Alarm         : bool = MemMapped.new(default=False, metadata={'description': _('Alarma Térmico ventilador de entrada'), 'tags': [ALARM, CO2]})
    outFanTerm1Alarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma Térmico ventilador de salida'),  'tags': [ALARM, CO2]})
    inFanTerm2Alarm         : bool = MemMapped.new(default=False, metadata={'description': _('AlarmaTérmico ventilador de entrada2'), 'tags': [ALARM, CO2]})
    outFanTerm2Alarm        : bool = MemMapped.new(default=False, metadata={'description': _('AlarmaTérmico ventilador de salida2'),  'tags': [ALARM, CO2]})
    resetAccumulatedWaterConsumption    : bool = MemMapped.new(default=False, metadata={'description': _('Reseatea el acumulado agua'), 'tags': [IODATA, HUMIDITY]}) # IODATA ?????
    resetAccumulatedC2H4Consumption     : bool = MemMapped.new(default=False, metadata={'description': _('Reseatea el acumulado C2H4'), 'tags': [IODATA, C2H4]}) # IODATA ?????
    petitionAccumulatedWaterConsumption : bool = MemMapped.new(default=False, metadata={'description': _('Hace una petición para saber el acumulado agua'), 'tags': [IODATA, HUMIDITY]}) # IODATA ?????
    petitionAccumulatedC2H4Consumption  : bool = MemMapped.new(default=False, metadata={'description': _('Hace una petición para saber el acumulado C2H4'), 'tags': [IODATA, C2H4]}) # IODATA ?????
    timeWithoutExtractionAlarm          : bool = MemMapped.new(default=False, metadata={'description': _('Tiempo sin extracción de aire'), 'tags': [ALARM]})
    telematicControlDisable             : bool = MemMapped.new(default=False, metadata={'description': _('No se puede poner en automático porque el control telemático está deshabilitado'), 'tags': [IODATA, ENABLED]}) # IODATA ?????????
    autoTelSelectorState                : bool = MemMapped.new(default=False, metadata={'description': _('Estado selector'), 'tags': [IODATA, SYSTEM]})
    tempExtSenBlockedAlarm              : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de temperatura exterior'), 'tags': [ALARM, SENSOR, TEMPERATURE]})
    humidityExtSenBlockedAlarm          : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de repetición de sensor de humedad exterior'),     'tags': [ALARM, SENSOR, HUMIDITY]})
    door1Open         : bool = MemMapped.new(default=False, metadata={'description': _('Puerta 1 abierta'), 'tags': [IODATA]})
    door2Open         : bool = MemMapped.new(default=False, metadata={'description': _('Puerta 2 abierta'), 'tags': [IODATA]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.outFanClixon2Alarm,
            self.inFanTerm1Alarm,
            self.outFanTerm1Alarm,
            self.inFanTerm2Alarm,
            self.outFanTerm2Alarm,
            self.resetAccumulatedWaterConsumption,
            self.resetAccumulatedC2H4Consumption,
            self.petitionAccumulatedWaterConsumption,
            self.petitionAccumulatedC2H4Consumption,
            self.timeWithoutExtractionAlarm,
            self.telematicControlDisable,
            self.autoTelSelectorState,
            self.tempExtSenBlockedAlarm,
            self.humidityExtSenBlockedAlarm,
            self.door1Open,
            self.door2Open,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.outFanClixon2Alarm                  = flags[0]
        self.inFanTerm1Alarm                     = flags[1]
        self.outFanTerm1Alarm                    = flags[2]
        self.inFanTerm2Alarm                     = flags[3]
        self.outFanTerm2Alarm                    = flags[4]
        self.resetAccumulatedWaterConsumption    = flags[5]
        self.resetAccumulatedC2H4Consumption     = flags[6]
        self.petitionAccumulatedWaterConsumption = flags[7]
        self.petitionAccumulatedC2H4Consumption  = flags[8]
        self.timeWithoutExtractionAlarm          = flags[9]
        self.telematicControlDisable             = flags[10]
        self.autoTelSelectorState                = flags[11]
        self.tempExtSenBlockedAlarm              = flags[12]
        self.humidityExtSenBlockedAlarm          = flags[13]
        self.door1Open                           = flags[14]
        self.door2Open                           = flags[15]

@dataclass
class Block14(MBusSerializable):
    lfan1      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación ventilador aerotermo 1'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfan2      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación ventilador aerotermo 2'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfan3      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación ventilador aerotermo 3'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfan4      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación ventilador aerotermo 4'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfan5      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación ventilador aerotermo 5'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfan6      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación ventilador aerotermo 6'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfan7      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación ventilador aerotermo 7'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfan8      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación ventilador aerotermo 8'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistor1 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación resitencia aerotermo 1'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistor2 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación resitencia aerotermo 2'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistor3 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación resitencia aerotermo 3'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistor4 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación resitencia aerotermo 4'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistor5 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación resitencia aerotermo 5'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistor6 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación resitencia aerotermo 6'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistor7 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación resitencia aerotermo 7'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistor8 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Activación resitencia aerotermo 8'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.lfan1,
            self.lfan2,
            self.lfan3,
            self.lfan4,
            self.lfan5,
            self.lfan6,
            self.lfan7,
            self.lfan8,
            self.lresistor1,
            self.lresistor2,
            self.lresistor3,
            self.lresistor4,
            self.lresistor5,
            self.lresistor6,
            self.lresistor7,
            self.lresistor8,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.lfan1      = flags[0]
        self.lfan2      = flags[1]
        self.lfan3      = flags[2]
        self.lfan4      = flags[3]
        self.lfan5      = flags[4]
        self.lfan6      = flags[5]
        self.lfan7      = flags[6]
        self.lfan8      = flags[7]
        self.lresistor1 = flags[8]
        self.lresistor2 = flags[9]
        self.lresistor3 = flags[10]
        self.lresistor4 = flags[11]
        self.lresistor5 = flags[12]
        self.lresistor6 = flags[13]
        self.lresistor7 = flags[14]
        self.lresistor8 = flags[15]

@dataclass
class Block15(MBusSerializable):
    lfanForced1      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado ventilador aerotermo 1'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfanForced2      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado ventilador aerotermo 2'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfanForced3      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado ventilador aerotermo 3'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfanForced4      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado ventilador aerotermo 4'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfanForced5      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado ventilador aerotermo 5'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfanForced6      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado ventilador aerotermo 6'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfanForced7      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado ventilador aerotermo 7'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lfanForced8      : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado ventilador aerotermo 8'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistorForced1 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado resistencia aerotermo 1'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistorForced2 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado resistencia aerotermo 2'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistorForced3 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado resistencia aerotermo 3'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistorForced4 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado resistencia aerotermo 4'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistorForced5 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado resistencia aerotermo 5'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistorForced6 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado resistencia aerotermo 6'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistorForced7 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado resistencia aerotermo 7'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    lresistorForced8 : bool = MemMapped.new(default=False, metadata={'description': _('Lectura Forzado resistencia aerotermo 8'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.lfanForced1,
            self.lfanForced2,
            self.lfanForced3,
            self.lfanForced4,
            self.lfanForced5,
            self.lfanForced6,
            self.lfanForced7,
            self.lfanForced8,
            self.lresistorForced1,
            self.lresistorForced2,
            self.lresistorForced3,
            self.lresistorForced4,
            self.lresistorForced5,
            self.lresistorForced6,
            self.lresistorForced7,
            self.lresistorForced8,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.lfanForced1      = flags[0]
        self.lfanForced2      = flags[1]
        self.lfanForced3      = flags[2]
        self.lfanForced4      = flags[3]
        self.lfanForced5      = flags[4]
        self.lfanForced6      = flags[5]
        self.lfanForced7      = flags[6]
        self.lfanForced8      = flags[7]
        self.lresistorForced1 = flags[8]
        self.lresistorForced2 = flags[9]
        self.lresistorForced3 = flags[10]
        self.lresistorForced4 = flags[11]
        self.lresistorForced5 = flags[12]
        self.lresistorForced6 = flags[13]
        self.lresistorForced7 = flags[14]
        self.lresistorForced8 = flags[15]

@dataclass
class Block16(MBusSerializable):
    airHeater1 : bool = MemMapped.new(default=False, metadata={'description': _('Activación aerotermo 1'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    airHeater2 : bool = MemMapped.new(default=False, metadata={'description': _('Activación aerotermo 2'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    airHeater3 : bool = MemMapped.new(default=False, metadata={'description': _('Activación aerotermo 3'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    airHeater4 : bool = MemMapped.new(default=False, metadata={'description': _('Activación aerotermo 4'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    airHeater5 : bool = MemMapped.new(default=False, metadata={'description': _('Activación aerotermo 5'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    airHeater6 : bool = MemMapped.new(default=False, metadata={'description': _('Activación aerotermo 6'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    airHeater7 : bool = MemMapped.new(default=False, metadata={'description': _('Activación aerotermo 7'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    airHeater8 : bool = MemMapped.new(default=False, metadata={'description': _('Activación aerotermo 8'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    _reserved_16_08 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 8'),    'tags': [RESERVED]})
    _reserved_16_09 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 9'),    'tags': [RESERVED]})
    _reserved_16_10 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 10'),   'tags': [RESERVED]})
    _reserved_16_11 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 11'),   'tags': [RESERVED]})
    _reserved_16_12 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 12'),   'tags': [RESERVED]})
    _reserved_16_13 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 13'),   'tags': [RESERVED]})
    _reserved_16_14 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 14'),   'tags': [RESERVED]})
    _reserved_16_15 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 15'),   'tags': [RESERVED]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.airHeater1,
            self.airHeater2,
            self.airHeater3,
            self.airHeater4,
            self.airHeater5,
            self.airHeater6,
            self.airHeater7,
            self.airHeater8,
            False, # self._reserved_16_08
            False, # self._reserved_16_09
            False, # self._reserved_16_10
            False, # self._reserved_16_11
            False, # self._reserved_16_12
            False, # self._reserved_16_13
            False, # self._reserved_16_14
            False, # self._reserved_16_15
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.airHeater1      = flags[0]
        self.airHeater2      = flags[1]
        self.airHeater3      = flags[2]
        self.airHeater4      = flags[3]
        self.airHeater5      = flags[4]
        self.airHeater6      = flags[5]
        self.airHeater7      = flags[6]
        self.airHeater8      = flags[7]
        # self._reserved_16_08 = flags[8]
        # self._reserved_16_09 = flags[9]
        # self._reserved_16_10 = flags[10]
        # self._reserved_16_11 = flags[11]
        # self._reserved_16_12 = flags[12]
        # self._reserved_16_13 = flags[13]
        # self._reserved_16_14 = flags[14]
        # self._reserved_16_15 = flags[15]

@dataclass
class Block17(MBusSerializable):
    eepromTypeToSave    : u16 = MemMapped.new(default=False, metadata={'description': _('Tipo de dato a guardar en eeprom'), 'tags': [IODATA, SYSTEM]})
    eepromAddressToSave : u16 = MemMapped.new(default=False, metadata={'description': _('Dirección a guardar en epprom'),    'tags': [IODATA, SYSTEM]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(self.eepromTypeToSave)
        encoder.add_16bit_uint(self.eepromAddressToSave)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.eepromTypeToSave    = decoder.decode_16bit_uint()
        self.eepromAddressToSave = decoder.decode_16bit_uint()

@dataclass
class Block18(MBusSerializable):
    C2H4Measure          : f32 = MemMapped.new(default=0.0, metadata={'description': _('Medida etileno'),               'units': 'ppm',            'tags': [IODATA, C2H4]})
    CO2Measure           : f32 = MemMapped.new(default=0.0, metadata={'description': _('Medida CO2'),                   'units': 'ppm',            'tags': [IODATA, CO2]})
    humidityInside       : f32 = MemMapped.new(default=0.0, metadata={'description': _('Humedad interior'),             'units': 'HR%',            'tags': [IODATA, HUMIDITY]})
    humidityOutside      : f32 = MemMapped.new(default=0.0, metadata={'description': _('Humedad exterior'),             'units': 'HR%',            'tags': [IODATA, HUMIDITY]})
    temperatureInside    : f32 = MemMapped.new(default=0.0, metadata={'description': _('Temperatura interior'),         'units': 'ºC',             'tags': [IODATA, TEMPERATURE]})
    temperatureOutside   : f32 = MemMapped.new(default=0.0, metadata={'description': _('Temperatura exterior'),         'units': 'ºC',             'tags': [IODATA, TEMPERATURE]})
    C2H4Flow             : f32 = MemMapped.new(default=0.0, metadata={'description': _('Medidor consumo de etileno'),   'units': 'L',              'tags': [IODATA, C2H4]})
    airPressure          : f32 = MemMapped.new(default=0.0, metadata={'description': _('Presión de aire'),              'units': 'bar', 'max': 10, 'tags': [IODATA, HUMIDITY]})
    waterPressure        : f32 = MemMapped.new(default=0.0, metadata={'description': _('Presión de agua'),              'units': 'bar', 'max': 6,  'tags': [IODATA, HUMIDITY]})
    waterFlow            : f32 = MemMapped.new(default=0.0, metadata={'description': _('Medidor consumo de agua'),      'units': 'L',              'tags': [IODATA, HUMIDITY]})
    _reserved282         : u16 = MemMapped.new(default=0,   metadata={'description': _('Reserved base+282'), 'tags': [RESERVED]})
    inFan1PowerMeasure   : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo ventilador entrada 1'), 'units': 'kw',             'tags': [IODATA, CO2]})
    outFan1PowerMeasure  : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo ventilador salida 1'),  'units': 'kw',             'tags': [IODATA, CO2]})
    inFan2PowerMeasure   : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo ventilador entrada 2'), 'units': 'kw',             'tags': [IODATA, CO2]})
    outFan2PowerMeasure  : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo ventilador salida 2'),  'units': 'kw',             'tags': [IODATA, CO2]})
    C2H4BottlePressure   : u16 = MemMapped.new(default=0,   metadata={'description': _("Presión botella etileno"),      'units': 'bar',            'tags': [IODATA, C2H4]})

    _reserved292         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+292"), 'tags': [RESERVED]})
    _reserved293         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+293"), 'tags': [RESERVED]})
    _reserved294         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+294"), 'tags': [RESERVED]})
    _reserved295         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+295"), 'tags': [RESERVED]})
    _reserved296         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+296"), 'tags': [RESERVED]})
    _reserved297         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+297"), 'tags': [RESERVED]})
    _reserved298         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+298"), 'tags': [RESERVED]})
    _reserved299         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+299"), 'tags': [RESERVED]})
    _reserved300         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+300"), 'tags': [RESERVED]})
    _reserved301         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+301"), 'tags': [RESERVED]})
    _reserved302         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+302"), 'tags': [RESERVED]})
    _reserved303         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+303"), 'tags': [RESERVED]})
    _reserved304         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+304"), 'tags': [RESERVED]})
    _reserved305         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+305"), 'tags': [RESERVED]})
    _reserved306         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+306"), 'tags': [RESERVED]})
    _reserved307         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+307"), 'tags': [RESERVED]})
    _reserved308         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+308"), 'tags': [RESERVED]})
    _reserved309         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+309"), 'tags': [RESERVED]})
    _reserved310         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+310"), 'tags': [RESERVED]})
    _reserved311         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+311"), 'tags': [RESERVED]})
    _reserved312         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+312"), 'tags': [RESERVED]})
    _reserved313         : u16 = MemMapped.new(default=0, metadata={'description': _("Reserved base+313"), 'tags': [RESERVED]})

    accumulatedWaterConsumption : u16 = MemMapped.new(default=0, metadata={'description': _('Conteo acumulado consumo de agua'),    'tags': [IODATA, HUMIDITY]})
    accumulatedC2H4Consumption  : u16 = MemMapped.new(default=0, metadata={'description': _('Conteo acumulado consumo de etileno'), 'tags': [IODATA, C2H4]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_32bit_float(self.C2H4Measure)
        encoder.add_32bit_float(self.CO2Measure)
        encoder.add_32bit_float(self.humidityInside)
        encoder.add_32bit_float(self.humidityOutside)
        encoder.add_32bit_float(self.temperatureInside)
        encoder.add_32bit_float(self.temperatureOutside)
        encoder.add_32bit_float(self.C2H4Flow)
        encoder.add_32bit_float(self.airPressure)
        encoder.add_32bit_float(self.waterPressure)
        encoder.add_32bit_float(self.waterFlow)
        encoder.add_16bit_uint(self._reserved282)
        encoder.add_32bit_float(self.inFan1PowerMeasure)
        encoder.add_32bit_float(self.outFan1PowerMeasure)
        encoder.add_32bit_float(self.inFan2PowerMeasure)
        encoder.add_32bit_float(self.outFan2PowerMeasure)
        encoder.add_16bit_uint(self.C2H4BottlePressure)

        encoder.add_16bit_uint(self._reserved292)
        encoder.add_16bit_uint(self._reserved293)
        encoder.add_16bit_uint(self._reserved294)
        encoder.add_16bit_uint(self._reserved295)
        encoder.add_16bit_uint(self._reserved296)
        encoder.add_16bit_uint(self._reserved297)
        encoder.add_16bit_uint(self._reserved298)
        encoder.add_16bit_uint(self._reserved299)
        encoder.add_16bit_uint(self._reserved300)
        encoder.add_16bit_uint(self._reserved301)
        encoder.add_16bit_uint(self._reserved302)
        encoder.add_16bit_uint(self._reserved303)
        encoder.add_16bit_uint(self._reserved304)
        encoder.add_16bit_uint(self._reserved305)
        encoder.add_16bit_uint(self._reserved306)
        encoder.add_16bit_uint(self._reserved307)
        encoder.add_16bit_uint(self._reserved308)
        encoder.add_16bit_uint(self._reserved309)
        encoder.add_16bit_uint(self._reserved310)
        encoder.add_16bit_uint(self._reserved311)
        encoder.add_16bit_uint(self._reserved312)
        encoder.add_16bit_uint(self._reserved313)

        encoder.add_16bit_uint(self.accumulatedWaterConsumption)
        encoder.add_16bit_uint(self.accumulatedC2H4Consumption)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.C2H4Measure                         = decoder.decode_32bit_float()
        self.CO2Measure                          = decoder.decode_32bit_float()
        self.humidityInside                      = decoder.decode_32bit_float()
        self.humidityOutside                     = decoder.decode_32bit_float()
        self.temperatureInside                   = decoder.decode_32bit_float()
        self.temperatureOutside                  = decoder.decode_32bit_float()
        self.C2H4Flow                            = decoder.decode_32bit_float()
        self.airPressure                         = decoder.decode_32bit_float()
        self.waterPressure                       = decoder.decode_32bit_float()
        self.waterFlow                           = decoder.decode_32bit_float()
        self._reserved282                        = decoder.decode_16bit_uint()
        self.inFan1PowerMeasure                  = decoder.decode_32bit_float()
        self.outFan1PowerMeasure                 = decoder.decode_32bit_float()
        self.inFan2PowerMeasure                  = decoder.decode_32bit_float()
        self.outFan2PowerMeasure                 = decoder.decode_32bit_float()
        self.C2H4BottlePressure                  = decoder.decode_16bit_uint()

        self._reserved292                        = decoder.decode_16bit_uint()
        self._reserved293                        = decoder.decode_16bit_uint()
        self._reserved294                        = decoder.decode_16bit_uint()
        self._reserved295                        = decoder.decode_16bit_uint()
        self._reserved296                        = decoder.decode_16bit_uint()
        self._reserved297                        = decoder.decode_16bit_uint()
        self._reserved298                        = decoder.decode_16bit_uint()
        self._reserved299                        = decoder.decode_16bit_uint()
        self._reserved300                        = decoder.decode_16bit_uint()
        self._reserved301                        = decoder.decode_16bit_uint()
        self._reserved302                        = decoder.decode_16bit_uint()
        self._reserved303                        = decoder.decode_16bit_uint()
        self._reserved304                        = decoder.decode_16bit_uint()
        self._reserved305                        = decoder.decode_16bit_uint()
        self._reserved306                        = decoder.decode_16bit_uint()
        self._reserved307                        = decoder.decode_16bit_uint()
        self._reserved308                        = decoder.decode_16bit_uint()
        self._reserved309                        = decoder.decode_16bit_uint()
        self._reserved310                        = decoder.decode_16bit_uint()
        self._reserved311                        = decoder.decode_16bit_uint()
        self._reserved312                        = decoder.decode_16bit_uint()
        self._reserved313                        = decoder.decode_16bit_uint()

        self.accumulatedWaterConsumption         = decoder.decode_16bit_uint()
        self.accumulatedC2H4Consumption          = decoder.decode_16bit_uint()

@dataclass
class Block19(MBusSerializable):
    fan1      : bool = MemMapped.new(default=False, metadata={'description': _('Activación ventilador aerotermo 1'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fan2      : bool = MemMapped.new(default=False, metadata={'description': _('Activación ventilador aerotermo 2'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fan3      : bool = MemMapped.new(default=False, metadata={'description': _('Activación ventilador aerotermo 3'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fan4      : bool = MemMapped.new(default=False, metadata={'description': _('Activación ventilador aerotermo 4'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fan5      : bool = MemMapped.new(default=False, metadata={'description': _('Activación ventilador aerotermo 5'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fan6      : bool = MemMapped.new(default=False, metadata={'description': _('Activación ventilador aerotermo 6'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fan7      : bool = MemMapped.new(default=False, metadata={'description': _('Activación ventilador aerotermo 7'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fan8      : bool = MemMapped.new(default=False, metadata={'description': _('Activación ventilador aerotermo 8'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistor1 : bool = MemMapped.new(default=False, metadata={'description': _('Activación resitencia aerotermo 1'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistor2 : bool = MemMapped.new(default=False, metadata={'description': _('Activación resitencia aerotermo 2'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistor3 : bool = MemMapped.new(default=False, metadata={'description': _('Activación resitencia aerotermo 3'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistor4 : bool = MemMapped.new(default=False, metadata={'description': _('Activación resitencia aerotermo 4'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistor5 : bool = MemMapped.new(default=False, metadata={'description': _('Activación resitencia aerotermo 5'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistor6 : bool = MemMapped.new(default=False, metadata={'description': _('Activación resitencia aerotermo 6'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistor7 : bool = MemMapped.new(default=False, metadata={'description': _('Activación resitencia aerotermo 7'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistor8 : bool = MemMapped.new(default=False, metadata={'description': _('Activación resitencia aerotermo 8'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.fan1,
            self.fan2,
            self.fan3,
            self.fan4,
            self.fan5,
            self.fan6,
            self.fan7,
            self.fan8,
            self.resistor1,
            self.resistor2,
            self.resistor3,
            self.resistor4,
            self.resistor5,
            self.resistor6,
            self.resistor7,
            self.resistor8,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.fan1      = flags[0]
        self.fan2      = flags[1]
        self.fan3      = flags[2]
        self.fan4      = flags[3]
        self.fan5      = flags[4]
        self.fan6      = flags[5]
        self.fan7      = flags[6]
        self.fan8      = flags[7]
        self.resistor1 = flags[8]
        self.resistor2 = flags[9]
        self.resistor3 = flags[10]
        self.resistor4 = flags[11]
        self.resistor5 = flags[12]
        self.resistor6 = flags[13]
        self.resistor7 = flags[14]
        self.resistor8 = flags[15]

@dataclass
class Block20(MBusSerializable):
    fanForced1      : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador aerotermo 1'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fanForced2      : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador aerotermo 2'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fanForced3      : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador aerotermo 3'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fanForced4      : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador aerotermo 4'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fanForced5      : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador aerotermo 5'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fanForced6      : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador aerotermo 6'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fanForced7      : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador aerotermo 7'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    fanForced8      : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador aerotermo 8'),  'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistorForced1 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado resistencia aerotermo 1'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistorForced2 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado resistencia aerotermo 2'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistorForced3 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado resistencia aerotermo 3'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistorForced4 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado resistencia aerotermo 4'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistorForced5 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado resistencia aerotermo 5'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistorForced6 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado resistencia aerotermo 6'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistorForced7 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado resistencia aerotermo 7'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    resistorForced8 : bool = MemMapped.new(default=False, metadata={'description': _('Forzado resistencia aerotermo 8'), 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.fanForced1,
            self.fanForced2,
            self.fanForced3,
            self.fanForced4,
            self.fanForced5,
            self.fanForced6,
            self.fanForced7,
            self.fanForced8,
            self.resistorForced1,
            self.resistorForced2,
            self.resistorForced3,
            self.resistorForced4,
            self.resistorForced5,
            self.resistorForced6,
            self.resistorForced7,
            self.resistorForced8,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.fanForced1      = flags[0]
        self.fanForced2      = flags[1]
        self.fanForced3      = flags[2]
        self.fanForced4      = flags[3]
        self.fanForced5      = flags[4]
        self.fanForced6      = flags[5]
        self.fanForced7      = flags[6]
        self.fanForced8      = flags[7]
        self.resistorForced1 = flags[8]
        self.resistorForced2 = flags[9]
        self.resistorForced3 = flags[10]
        self.resistorForced4 = flags[11]
        self.resistorForced5 = flags[12]
        self.resistorForced6 = flags[13]
        self.resistorForced7 = flags[14]
        self.resistorForced8 = flags[15]

@dataclass
class Block21(MBusSerializable):
    airHeater1FlowAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma sensor flujo aerotermo 1'),       'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater2FlowAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma sensor flujo aerotermo 2'),       'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater3FlowAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma sensor flujo aerotermo 3'),       'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater4FlowAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma sensor flujo aerotermo 4'),       'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater5FlowAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma sensor flujo aerotermo 5'),       'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater6FlowAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma sensor flujo aerotermo 6'),       'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater7FlowAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma sensor flujo aerotermo 7'),       'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater8FlowAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma sensor flujo aerotermo 8'),       'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater1TermAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma térmico ventilador aerotermo 1'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater2TermAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma térmico ventilador aerotermo 2'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater3TermAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma térmico ventilador aerotermo 3'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater4TermAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma térmico ventilador aerotermo 4'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater5TermAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma térmico ventilador aerotermo 5'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater6TermAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma térmico ventilador aerotermo 6'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater7TermAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma térmico ventilador aerotermo 7'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater8TermAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma térmico ventilador aerotermo 8'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.airHeater1FlowAlarm,
            self.airHeater2FlowAlarm,
            self.airHeater3FlowAlarm,
            self.airHeater4FlowAlarm,
            self.airHeater5FlowAlarm,
            self.airHeater6FlowAlarm,
            self.airHeater7FlowAlarm,
            self.airHeater8FlowAlarm,
            self.airHeater1TermAlarm,
            self.airHeater2TermAlarm,
            self.airHeater3TermAlarm,
            self.airHeater4TermAlarm,
            self.airHeater5TermAlarm,
            self.airHeater6TermAlarm,
            self.airHeater7TermAlarm,
            self.airHeater8TermAlarm,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.airHeater1FlowAlarm = flags[0]
        self.airHeater2FlowAlarm = flags[1]
        self.airHeater3FlowAlarm = flags[2]
        self.airHeater4FlowAlarm = flags[3]
        self.airHeater5FlowAlarm = flags[4]
        self.airHeater6FlowAlarm = flags[5]
        self.airHeater7FlowAlarm = flags[6]
        self.airHeater8FlowAlarm = flags[7]
        self.airHeater1TermAlarm = flags[8]
        self.airHeater2TermAlarm = flags[9]
        self.airHeater3TermAlarm = flags[10]
        self.airHeater4TermAlarm = flags[11]
        self.airHeater5TermAlarm = flags[12]
        self.airHeater6TermAlarm = flags[13]
        self.airHeater7TermAlarm = flags[14]
        self.airHeater8TermAlarm = flags[15]

@dataclass
class Block22(MBusSerializable):
    airHeater1ClixonAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon ventilador aerotermo 1'),         'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater2ClixonAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon ventilador aerotermo 2'),         'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater3ClixonAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon ventilador aerotermo 3'),         'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater4ClixonAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon ventilador aerotermo 4'),         'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater5ClixonAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon ventilador aerotermo 5'),         'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater6ClixonAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon ventilador aerotermo 6'),         'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater7ClixonAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon ventilador aerotermo 7'),         'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater8ClixonAlarm    : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon ventilador aerotermo 8'),         'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater1OperationAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma funcionamiento ventilador aerotermo 1'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater2OperationAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma funcionamiento ventilador aerotermo 2'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater3OperationAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma funcionamiento ventilador aerotermo 3'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater4OperationAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma funcionamiento ventilador aerotermo 4'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater5OperationAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma funcionamiento ventilador aerotermo 5'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater6OperationAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma funcionamiento ventilador aerotermo 6'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater7OperationAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma funcionamiento ventilador aerotermo 7'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater8OperationAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma funcionamiento ventilador aerotermo 8'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.airHeater1ClixonAlarm,
            self.airHeater2ClixonAlarm,
            self.airHeater3ClixonAlarm,
            self.airHeater4ClixonAlarm,
            self.airHeater5ClixonAlarm,
            self.airHeater6ClixonAlarm,
            self.airHeater7ClixonAlarm,
            self.airHeater8ClixonAlarm,
            self.airHeater1OperationAlarm,
            self.airHeater2OperationAlarm,
            self.airHeater3OperationAlarm,
            self.airHeater4OperationAlarm,
            self.airHeater5OperationAlarm,
            self.airHeater6OperationAlarm,
            self.airHeater7OperationAlarm,
            self.airHeater8OperationAlarm,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.airHeater1ClixonAlarm    = flags[0]
        self.airHeater2ClixonAlarm    = flags[1]
        self.airHeater3ClixonAlarm    = flags[2]
        self.airHeater4ClixonAlarm    = flags[3]
        self.airHeater5ClixonAlarm    = flags[4]
        self.airHeater6ClixonAlarm    = flags[5]
        self.airHeater7ClixonAlarm    = flags[6]
        self.airHeater8ClixonAlarm    = flags[7]
        self.airHeater1OperationAlarm = flags[8]
        self.airHeater2OperationAlarm = flags[9]
        self.airHeater3OperationAlarm = flags[10]
        self.airHeater4OperationAlarm = flags[11]
        self.airHeater5OperationAlarm = flags[12]
        self.airHeater6OperationAlarm = flags[13]
        self.airHeater7OperationAlarm = flags[14]
        self.airHeater8OperationAlarm = flags[15]

@dataclass
class Block23(MBusSerializable):
    airHeater1ClixonResistorAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon resistencia aerotermo 1'),   'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater2ClixonResistorAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon resistencia aerotermo 2'),   'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater3ClixonResistorAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon resistencia aerotermo 3'),   'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater4ClixonResistorAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon resistencia aerotermo 4'),   'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater5ClixonResistorAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon resistencia aerotermo 5'),   'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater6ClixonResistorAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon resistencia aerotermo 6'),   'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater7ClixonResistorAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon resistencia aerotermo 7'),   'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater8ClixonResistorAlarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma clixon resistencia aerotermo 8'),   'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater1NeutralAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma corriente por neutro aerotermo 1'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater2NeutralAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma corriente por neutro aerotermo 2'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater3NeutralAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma corriente por neutro aerotermo 3'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater4NeutralAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma corriente por neutro aerotermo 4'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater5NeutralAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma corriente por neutro aerotermo 5'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater6NeutralAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma corriente por neutro aerotermo 6'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater7NeutralAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma corriente por neutro aerotermo 7'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})
    airHeater8NeutralAlarm        : bool = MemMapped.new(default=False, metadata={'description': _('Alarma corriente por neutro aerotermo 8'), 'tags': [ALARM, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.airHeater1ClixonResistorAlarm,
            self.airHeater2ClixonResistorAlarm,
            self.airHeater3ClixonResistorAlarm,
            self.airHeater4ClixonResistorAlarm,
            self.airHeater5ClixonResistorAlarm,
            self.airHeater6ClixonResistorAlarm,
            self.airHeater7ClixonResistorAlarm,
            self.airHeater8ClixonResistorAlarm,
            self.airHeater1NeutralAlarm,
            self.airHeater2NeutralAlarm,
            self.airHeater3NeutralAlarm,
            self.airHeater4NeutralAlarm,
            self.airHeater5NeutralAlarm,
            self.airHeater6NeutralAlarm,
            self.airHeater7NeutralAlarm,
            self.airHeater8NeutralAlarm,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.airHeater1ClixonResistorAlarm = flags[0]
        self.airHeater2ClixonResistorAlarm = flags[1]
        self.airHeater3ClixonResistorAlarm = flags[2]
        self.airHeater4ClixonResistorAlarm = flags[3]
        self.airHeater5ClixonResistorAlarm = flags[4]
        self.airHeater6ClixonResistorAlarm = flags[5]
        self.airHeater7ClixonResistorAlarm = flags[6]
        self.airHeater8ClixonResistorAlarm = flags[7]
        self.airHeater1NeutralAlarm        = flags[8]
        self.airHeater2NeutralAlarm        = flags[9]
        self.airHeater3NeutralAlarm        = flags[10]
        self.airHeater4NeutralAlarm        = flags[11]
        self.airHeater5NeutralAlarm        = flags[12]
        self.airHeater6NeutralAlarm        = flags[13]
        self.airHeater7NeutralAlarm        = flags[14]
        self.airHeater8NeutralAlarm        = flags[15]

@dataclass
class Block24(MBusSerializable):
    heater1PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 1'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater2PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 2'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater3PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 3'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater4PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 4'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater5PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 5'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater6PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 6'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater7PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 7'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater8PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 8'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_32bit_float(self.heater1PowerMeasure)
        encoder.add_32bit_float(self.heater2PowerMeasure)
        encoder.add_32bit_float(self.heater3PowerMeasure)
        encoder.add_32bit_float(self.heater4PowerMeasure)
        encoder.add_32bit_float(self.heater5PowerMeasure)
        encoder.add_32bit_float(self.heater6PowerMeasure)
        encoder.add_32bit_float(self.heater7PowerMeasure)
        encoder.add_32bit_float(self.heater8PowerMeasure)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.heater1PowerMeasure = decoder.decode_32bit_float()
        self.heater2PowerMeasure = decoder.decode_32bit_float()
        self.heater3PowerMeasure = decoder.decode_32bit_float()
        self.heater4PowerMeasure = decoder.decode_32bit_float()
        self.heater5PowerMeasure = decoder.decode_32bit_float()
        self.heater6PowerMeasure = decoder.decode_32bit_float()
        self.heater7PowerMeasure = decoder.decode_32bit_float()
        self.heater8PowerMeasure = decoder.decode_32bit_float()

@dataclass
class Block25(MBusSerializable):
    forcedSafetyRelayReset        : bool = MemMapped.new(default=False, metadata={'description': _('Forzado del rele de rearme'),      'tags': [PARAM, FORCED]})
    forcedInputFan1               : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador entrada 1'),    'tags': [PARAM, FORCED]})
    forcedInputFan2               : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador entrada 2'),    'tags': [PARAM, FORCED]})
    forcedOutputFan1              : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador salida 1'),     'tags': [PARAM, FORCED]})
    forcedOutputFan2              : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador salida 2'),     'tags': [PARAM, FORCED]})
    forcedAeroheaters             : bool = MemMapped.new(default=False, metadata={'description': _('Forzado aerotermos'),              'tags': [PARAM, FORCED]})
    forcedHumidityWatersValves    : bool = MemMapped.new(default=False, metadata={'description': _('Forzado humedad'),                 'tags': [PARAM, FORCED]})
    forcedCoolingRequest          : bool = MemMapped.new(default=False, metadata={'description': _('Forzado pedido de frío'),          'tags': [PARAM, FORCED]})
    forcedHeatingRequest          : bool = MemMapped.new(default=False, metadata={'description': _('Forzado pedido de calor'),         'tags': [PARAM, FORCED]})
    forcedControlCoolingRequest   : bool = MemMapped.new(default=False, metadata={'description': _('Forzado pedido control de frío'),  'tags': [PARAM, FORCED]})
    forcedControlHeatingRequest   : bool = MemMapped.new(default=False, metadata={'description': _('Forzado pedido control calor'),    'tags': [PARAM, FORCED]})
    forcedEvaporatorFanActivator  : bool = MemMapped.new(default=False, metadata={'description': _('Forzado ventilador evaporizador'), 'tags': [PARAM, FORCED]})
    forcedAlarmSet                : bool = MemMapped.new(default=False, metadata={'description': _('Forzado alarma'),                  'tags': [PARAM, FORCED]})
    forcedEthylene                : bool = MemMapped.new(default=False, metadata={'description': _('Forzado etileno'),                 'tags': [PARAM, FORCED]})
    forcedHumidityAirValves       : bool = MemMapped.new(default=False, metadata={'description': _('Forzado boquilla aire'),           'tags': [PARAM, FORCED]})
    fanAeroheaterState            : bool = MemMapped.new(default=False, metadata={'description': _('Estado ventilador de los aerotermos'), 'tags': [PARAM, CO2]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.forcedSafetyRelayReset,
            self.forcedInputFan1,
            self.forcedInputFan2,
            self.forcedOutputFan1,
            self.forcedOutputFan2,
            self.forcedAeroheaters,
            self.forcedHumidityWatersValves,
            self.forcedCoolingRequest,
            self.forcedHeatingRequest,
            self.forcedControlCoolingRequest,
            self.forcedControlHeatingRequest,
            self.forcedEvaporatorFanActivator,
            self.forcedAlarmSet,
            self.forcedEthylene,
            self.forcedHumidityAirValves,
            self.fanAeroheaterState,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.forcedSafetyRelayReset       = flags[0]
        self.forcedInputFan1              = flags[1]
        self.forcedInputFan2              = flags[2]
        self.forcedOutputFan1             = flags[3]
        self.forcedOutputFan2             = flags[4]
        self.forcedAeroheaters            = flags[5]
        self.forcedHumidityWatersValves   = flags[6]
        self.forcedCoolingRequest         = flags[7]
        self.forcedHeatingRequest         = flags[8]
        self.forcedControlCoolingRequest  = flags[9]
        self.forcedControlHeatingRequest  = flags[10]
        self.forcedEvaporatorFanActivator = flags[11]
        self.forcedAlarmSet               = flags[12]
        self.forcedEthylene               = flags[13]
        self.forcedHumidityAirValves      = flags[14]
        self.fanAeroheaterState           = flags[15]

@dataclass
class Block26(MBusSerializable):
    humidityValvesActivated        : bool = MemMapped.new(default=False, metadata={'description': _('Electroválvula humedad activada'),       'tags': [IODATA, HUMIDITY]})
    ethyleneValvesActivated        : bool = MemMapped.new(default=False, metadata={'description': _('Electroválvula etileno activada'),       'tags': [IODATA, C2H4]})
    fanIn1Activated                : bool = MemMapped.new(default=False, metadata={'description': _('Ventilador entrada activado'),           'tags': [IODATA, CO2]})
    fanOut1Activated               : bool = MemMapped.new(default=False, metadata={'description': _('Ventilador salida activado'),            'tags': [IODATA, CO2]})
    finalInjectionMessageActivated : bool = MemMapped.new(default=False, metadata={'description': _('Mensaje inicial inyección'),             'tags': [IODATA, C2H4, GAS_BALANCE]})
    door1Blocked                   : bool = MemMapped.new(default=False, metadata={'description': _('Puerta 1 bloqueada'),                    'tags': [ALARM]}) # ALARM ???
    door2Blocked                   : bool = MemMapped.new(default=False, metadata={'description': _('Puerta 2 bloqueada'),                    'tags': [ALARM]}) # ALARM ???
    cycleInit                      : bool = MemMapped.new(default=False, metadata={'description': _('Inicio de ciclo'),                       'tags': [IODATA, C2H4, GAS_BALANCE]})
    emptyC2H4Bottle                : bool = MemMapped.new(default=False, metadata={'description': _('Alarma botella vacia etileno'),          'tags': [ALARM_CFG, C2H4]})
    preColdHumidityInjectionState  : bool = MemMapped.new(default=False, metadata={'description': _('Activación inyección humedad pre frío'), 'tags': [IODATA, HUMIDITY]})
    maintenanceInjection           : bool = MemMapped.new(default=False, metadata={'description': _('Activación de inyección mantenimiento'), 'tags': [IODATA, C2H4, GAS_BALANCE]})
    extraction                     : bool = MemMapped.new(default=False, metadata={'description': _('Extracción de etileno en conservación'), 'tags': [IODATA, C2H4]})
    fanIn2Activated                : bool = MemMapped.new(default=False, metadata={'description': _('Ventilador entrada 2 activado'),         'tags': [IODATA, CO2]})
    fanOut2Activated               : bool = MemMapped.new(default=False, metadata={'description': _('Ventilador salida 2 activado'),          'tags': [IODATA, CO2]})
    HumidityAirValves              : bool = MemMapped.new(default=False, metadata={'description': _('Boquilla aire'),                         'tags': [IODATA, HUMIDITY]})
    heatActivated                  : bool = MemMapped.new(default=False, metadata={'description': _('Calor activado'),                        'tags': [IODATA, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.humidityValvesActivated,
            self.ethyleneValvesActivated,
            self.fanIn1Activated,
            self.fanOut1Activated,
            self.finalInjectionMessageActivated,
            self.door1Blocked,
            self.door2Blocked,
            self.cycleInit,
            self.emptyC2H4Bottle,
            self.preColdHumidityInjectionState,
            self.maintenanceInjection,
            self.extraction,
            self.fanIn2Activated,
            self.fanOut2Activated,
            self.HumidityAirValves,
            self.heatActivated,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.humidityValvesActivated         = flags[0]
        self.ethyleneValvesActivated         = flags[1]
        self.fanIn1Activated                 = flags[2]
        self.fanOut1Activated                = flags[3]
        self.finalInjectionMessageActivated  = flags[4]
        self.door1Blocked                    = flags[5]
        self.door2Blocked                    = flags[6]
        self.cycleInit                       = flags[7]
        self.emptyC2H4Bottle                 = flags[8]
        self.preColdHumidityInjectionState   = flags[9]
        self.maintenanceInjection            = flags[10]
        self.extraction                      = flags[11]
        self.fanIn2Activated                 = flags[12]
        self.fanOut2Activated                = flags[13]
        self.HumidityAirValves               = flags[14]
        self.heatActivated                   = flags[15]

@dataclass
class Block27(MBusSerializable):
    coldActivated            : bool = MemMapped.new(default=False, metadata={'description': _('Frío activado'),            'tags': [IODATA, TEMPERATURE]})
    evaporatorFanActivator   : bool = MemMapped.new(default=False, metadata={'description': _('Evaporador activado'),      'tags': [IODATA, SYSTEM]})
    defrostActivated         : bool = MemMapped.new(default=False, metadata={'description': _('Defrost activado'),         'tags': [IODATA, SYSTEM]})
    autoselectorStates       : bool = MemMapped.new(default=False, metadata={'description': _('Autoselector activado'),    'tags': [IODATA, SYSTEM]})
    alarmState               : bool = MemMapped.new(default=False, metadata={'description': _('Alarma activada'),          'tags': [IODATA, SYSTEM]})
    emergencyStopState       : bool = MemMapped.new(default=False, metadata={'description': _('Mensaje relé de emergencia desarmado'),            'tags': [IODATA, ALARM_CFG]})
    aeroheatersGeneralForced : bool = MemMapped.new(default=False, metadata={'description': _('Forzado salida general aerotermos'),               'tags': [IODATA, FORCED]})
    aeroheatersGeneralState  : bool = MemMapped.new(default=False, metadata={'description': _('Estado salida general de control  de aerotermos'), 'tags': [IODATA, TEMPERATURE]})
    humidityGeneralForced    : bool = MemMapped.new(default=False, metadata={'description': _('Forzado salida general humedad'),                  'tags': [IODATA, FORCED]})
    humidityGeneralState     : bool = MemMapped.new(default=False, metadata={'description': _('Estado salida general de control  de humedad'),    'tags': [IODATA, HUMIDITY]})
    manualPowerCutMessage    : bool = MemMapped.new(default=False, metadata={'description': _('Mensaje de corte de corriente manual'),            'tags': [IODATA, SYSTEM]})
    generalSwichState        : bool = MemMapped.new(default=False, metadata={'description': _('Estado interruptor general'),                      'tags': [IODATA, SYSTEM]})
    C2H4LowPressureAlarm     : bool = MemMapped.new(default=False, metadata={'description': _('Mensaje baja presión de etileno'),                 'tags': [IODATA, SENSOR, C2H4]})
    tempSenExtFailure1Alarm      : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor exterior de temperatura 1'), 'tags': [ALARM, SENSOR, TEMPERATURE]})
    tempSenExtFFailure2Alarm     : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor exterior de temperatura 2'), 'tags': [ALARM, SENSOR, TEMPERATURE]})
    humidityExtFSenFailure1Alarm : bool = MemMapped.new(default=False, metadata={'description': _('Alarma de fallo de sensor exterior de humedad 1'),     'tags': [ALARM, SENSOR, HUMIDITY]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.coldActivated,
            self.evaporatorFanActivator,
            self.defrostActivated,
            self.autoselectorStates,
            self.alarmState,
            self.emergencyStopState,
            self.aeroheatersGeneralForced,
            self.aeroheatersGeneralState,
            self.humidityGeneralForced,
            self.humidityGeneralState,
            self.manualPowerCutMessage,
            self.generalSwichState,
            self.C2H4LowPressureAlarm,
            self.tempSenExtFailure1Alarm,
            self.tempSenExtFFailure2Alarm,
            self.humidityExtFSenFailure1Alarm,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.coldActivated            = flags[0]
        self.evaporatorFanActivator   = flags[1]
        self.defrostActivated         = flags[2]
        self.autoselectorStates       = flags[3]
        self.alarmState               = flags[4]
        self.emergencyStopState       = flags[5]
        self.aeroheatersGeneralForced = flags[6]
        self.aeroheatersGeneralState  = flags[7]
        self.humidityGeneralForced    = flags[8]
        self.humidityGeneralState     = flags[9]
        self.manualPowerCutMessage    = flags[10]
        self.generalSwichState        = flags[11]
        self.C2H4LowPressureAlarm     = flags[12]
        self.tempSenExtFailure1Alarm      = flags[13]
        self.tempSenExtFFailure2Alarm     = flags[14]
        self.humidityExtFSenFailure1Alarm = flags[15]

@dataclass
class Block28(MBusSerializable):
    ethyleneBottlePressure : u16 = MemMapped.new(default=0,   metadata={'description': _('Presión botella etileno'), 'units': 'bar',                 'tags': [IODATA, C2H4]}) # Duplicated C2H4 ??
    difTemp1               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 1'),  'tags': [IODATA, TEMPERATURE]})
    difTemp2               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 2'),  'tags': [IODATA, TEMPERATURE]})
    difTemp3               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 3'),  'tags': [IODATA, TEMPERATURE]})
    difTemp4               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 4'),  'tags': [IODATA, TEMPERATURE]})
    difTemp5               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 5'),  'tags': [IODATA, TEMPERATURE]})
    difTemp6               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 6'),  'tags': [IODATA, TEMPERATURE]})
    difTemp7               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 7'),  'tags': [IODATA, TEMPERATURE]})
    difTemp8               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 8'),  'tags': [IODATA, TEMPERATURE]})
    difTemp9               : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 9'),  'tags': [IODATA, TEMPERATURE]})
    difTemp10              : f32 = MemMapped.new(default=0.0, metadata={'description': _('Diferencia entre temperatura y setpoint de la cámara 10'), 'tags': [IODATA, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(self.ethyleneBottlePressure)
        encoder.add_32bit_float(self.difTemp1)
        encoder.add_32bit_float(self.difTemp2)
        encoder.add_32bit_float(self.difTemp3)
        encoder.add_32bit_float(self.difTemp4)
        encoder.add_32bit_float(self.difTemp5)
        encoder.add_32bit_float(self.difTemp6)
        encoder.add_32bit_float(self.difTemp7)
        encoder.add_32bit_float(self.difTemp8)
        encoder.add_32bit_float(self.difTemp9)
        encoder.add_32bit_float(self.difTemp10)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.ethyleneBottlePressure = decoder.decode_16bit_uint()
        self.difTemp1  = decoder.decode_32bit_float()
        self.difTemp2  = decoder.decode_32bit_float()
        self.difTemp3  = decoder.decode_32bit_float()
        self.difTemp4  = decoder.decode_32bit_float()
        self.difTemp5  = decoder.decode_32bit_float()
        self.difTemp6  = decoder.decode_32bit_float()
        self.difTemp7  = decoder.decode_32bit_float()
        self.difTemp8  = decoder.decode_32bit_float()
        self.difTemp9  = decoder.decode_32bit_float()
        self.difTemp10 = decoder.decode_32bit_float()

@dataclass
class Block29(MBusSerializable):
    actTemp1        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp2        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp3        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp4        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp5        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp6        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp7        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp8        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp9        : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    actTemp10       : bool = MemMapped.new(default=False, metadata={'description': _('Permite activar temperatura en la cámara'), 'tags': [IODATA, TEMPERATURE]})
    airPressureSensorState   : bool = MemMapped.new(default=False, metadata={'description': _('Estado del sensor de presión de aire'), 'tags': [IODATA, ALARM_CFG, HUMIDITY]})
    waterPressureSensorState : bool = MemMapped.new(default=False, metadata={'description': _('Estado del sensor de presión de agua'), 'tags': [IODATA, ALARM_CFG, HUMIDITY]})
    heatingPetition : bool = MemMapped.new(default=False, metadata={'description': _(' Petición de calor de la cámara'),               'tags': [IODATA, TEMPERATURE]})
    C2H4FailAlarm   : bool = MemMapped.new(default=False, metadata={'description': _('Alarma fallo en inyección de etileno'),          'tags': [IODATA, C2H4]})
    _reserved_29_14 : bool = MemMapped.new(default=False, metadata={'description': _('Reserved bit 14'), 'tags': [RESERVED]})
    resetRelayState : bool = MemMapped.new(default=False, metadata={'description': _('Estado relé de rearme'), 'tags': [IODATA, SYSTEM]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(from_bits([
            self.actTemp1,
            self.actTemp2,
            self.actTemp3,
            self.actTemp4,
            self.actTemp5,
            self.actTemp6,
            self.actTemp7,
            self.actTemp8,
            self.actTemp9,
            self.actTemp10,
            self.airPressureSensorState,
            self.waterPressureSensorState,
            self.heatingPetition,
            self.C2H4FailAlarm,
            False, # self._reserved_29_14,
            self.resetRelayState,
        ]))

    def _decode(self, decoder: BinaryPayloadDecoder):
        flags = to_bits(decoder.decode_16bit_uint(), 16)
        self.actTemp1        = flags[0]
        self.actTemp2        = flags[1]
        self.actTemp3        = flags[2]
        self.actTemp4        = flags[3]
        self.actTemp5        = flags[4]
        self.actTemp6        = flags[5]
        self.actTemp7        = flags[6]
        self.actTemp8        = flags[7]
        self.actTemp9        = flags[8]
        self.actTemp10       = flags[9]
        self.airPressureSensorState   = flags[10]
        self.waterPressureSensorState = flags[11]
        self.heatingPetition          = flags[12]
        self.C2H4FailAlarm            = flags[13]
        # self._reserved_29_14 = flags[14]
        self.resetRelayState = flags[15]

@dataclass
class Block30(MBusSerializable):
    activationTimeTemperature : u16 = MemMapped.new(default=0,   metadata={'description': _('Tiempo que se activa las resistencias'),  'tags': [IODATA, TEMPERATURE]})

    C2H4MeasureRaw            : f32 = MemMapped.new(default=0-0, metadata={'description': _('Medida etileno'),       'tags': [RESERVED]}) # duplicated
    CO2MeasureRaw             : f32 = MemMapped.new(default=0-0, metadata={'description': _('Medida CO2'),           'tags': [RESERVED]}) # duplicated
    humidityInsideRaw         : f32 = MemMapped.new(default=0-0, metadata={'description': _('Humedad interior'),     'tags': [RESERVED]}) # duplicated
    humidityOutsideRaw        : f32 = MemMapped.new(default=0-0, metadata={'description': _('Humedad exterior'),     'tags': [RESERVED]}) # duplicated
    temperatureInsideRaw      : f32 = MemMapped.new(default=0-0, metadata={'description': _('Temperatura interior'), 'tags': [RESERVED]}) # duplicated
    temperatureOutsideRaw     : f32 = MemMapped.new(default=0-0, metadata={'description': _('Temperatura exterior'), 'tags': [RESERVED]}) # duplicated

    totalPower                : f32 = MemMapped.new(default=0.0, metadata={'description': _('Potencia total de la instalación'),   'tags': [IODATA, TEMPERATURE]})
    maxTotalPower             : f32 = MemMapped.new(default=0.0, metadata={'description': _('Potencia total máxima de la cámara'), 'tags': [IODATA, TEMPERATURE]})
    ethyleneCorrector         : f32 = MemMapped.new(default=0.0, metadata={'description': _('Correcion sensor etileno'),           'tags': [IODATA, TEMPERATURE]})

    def _encode(self, encoder: BinaryPayloadBuilder):
        encoder.add_16bit_uint(self.activationTimeTemperature)
        encoder.add_32bit_float(self.C2H4MeasureRaw)
        encoder.add_32bit_float(self.CO2MeasureRaw)
        encoder.add_32bit_float(self.humidityInsideRaw)
        encoder.add_32bit_float(self.humidityOutsideRaw)
        encoder.add_32bit_float(self.temperatureInsideRaw)
        encoder.add_32bit_float(self.temperatureOutsideRaw)
        encoder.add_32bit_float(self.totalPower)
        encoder.add_32bit_float(self.maxTotalPower)
        encoder.add_32bit_float(self.ethyleneCorrector)

    def _decode(self, decoder: BinaryPayloadDecoder):
        self.activationTimeTemperature = decoder.decode_16bit_uint()
        self.C2H4MeasureRaw            = decoder.decode_32bit_float()
        self.CO2MeasureRaw             = decoder.decode_32bit_float()
        self.humidityInsideRaw         = decoder.decode_32bit_float()
        self.humidityOutsideRaw        = decoder.decode_32bit_float()
        self.temperatureInsideRaw      = decoder.decode_32bit_float()
        self.temperatureOutsideRaw     = decoder.decode_32bit_float()
        self.totalPower                = decoder.decode_32bit_float()
        self.maxTotalPower             = decoder.decode_32bit_float()
        self.ethyleneCorrector         = decoder.decode_32bit_float()