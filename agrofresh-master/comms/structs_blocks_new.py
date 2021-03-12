from dataclasses import (
    dataclass,
    field,
)
from django.utils.translation import gettext_noop as _
from .mbus_types import (
    MemMapped,
    EEPROM,
)
from .mbus_types_new import (
    MBusSerializable,
    MBusBitField,
    MBusStruct,
    i16, i32, u16, u32, f32,
)
from .tags import *
import math


@dataclass
class PIDControllerParams(MBusStruct):
    pCoefficient: i16 = EEPROM.new(default=0, metadata={'description': _('Ganancia proporcional')})
    iCoefficient: i16 = EEPROM.new(default=0, metadata={'description': _('Ganancia integral')})
    dCoefficient: i16 = EEPROM.new(default=0, metadata={'description': _('Ganancia derivativa')})
    # reference: i16  = EEPROM.new(default=0, metadata={'description': _('Referencia'), 'tags': [PARAM]})


@dataclass
class SensorParams(MBusStruct):
    units: str   = field(default='', metadata={'description': _('Unidades de sensor')})

    # rango
    minimum: i16 = EEPROM.new(default=0, metadata={'description': _('Mínimo rango sensor')})
    maximum: i16 = EEPROM.new(default=0, metadata={'description': _('Máximo rango sensor')})

    # calibración
    zero: i16 = EEPROM.new(default=0, metadata={'description': _('Ajuste zero sensor')})
    span: i16 = EEPROM.new(default=0, metadata={'description': _('Ajuste span sensor')})


@dataclass
class DateTime(MBusStruct):
    year   : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (año)')})
    month  : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (mes)')})
    day    : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (día)')})
    hour   : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (hora)')})
    minute : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (min)')})
    second : u16 = EEPROM.new(default=0, metadata={'description': _('Configuración de fecha y hora (sec)')})


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
class Block00(MBusBitField):
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


@dataclass
class Block01(MBusBitField):
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


@dataclass
class Block02(MBusBitField):
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



@dataclass
class Block03(MBusStruct):
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

@dataclass
class Block04(MBusBitField):
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

@dataclass
class Block05(MBusStruct):
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


@dataclass
class Block06(MBusBitField):
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


@dataclass
class Block07(MBusBitField):
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


@dataclass
class Block08(MBusBitField):
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


@dataclass
class Block09(MBusBitField):
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


@dataclass
class Block10(MBusBitField):
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


@dataclass
class Block11(MBusBitField):
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


@dataclass
class Block12(MBusBitField):
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


@dataclass
class Block13(MBusBitField):
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


@dataclass
class Block14(MBusBitField):
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


@dataclass
class Block15(MBusBitField):
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


@dataclass
class Block16(MBusBitField):
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


@dataclass
class Block17(MBusStruct):
    eepromTypeToSave    : u16 = MemMapped.new(default=False, metadata={'description': _('Tipo de dato a guardar en eeprom'), 'tags': [IODATA, SYSTEM]})
    eepromAddressToSave : u16 = MemMapped.new(default=False, metadata={'description': _('Dirección a guardar en epprom'),    'tags': [IODATA, SYSTEM]})


@dataclass
class Block18(MBusStruct):
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


@dataclass
class Block19(MBusBitField):
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


@dataclass
class Block20(MBusBitField):
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


@dataclass
class Block21(MBusBitField):
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


@dataclass
class Block22(MBusBitField):
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


@dataclass
class Block23(MBusBitField):
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


@dataclass
class Block24(MBusStruct):
    heater1PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 1'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater2PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 2'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater3PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 3'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater4PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 4'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater5PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 5'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater6PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 6'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater7PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 7'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})
    heater8PowerMeasure : f32 = MemMapped.new(default=0.0, metadata={'description': _('Consumo aerotermo 8'), 'units': 'kw', 'tags': [IODATA, AIR_HEATER, TEMPERATURE]})


@dataclass
class Block25(MBusBitField):
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



@dataclass
class Block26(MBusBitField):
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


@dataclass
class Block27(MBusBitField):
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


@dataclass
class Block28(MBusStruct):
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


@dataclass
class Block29(MBusBitField):
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


@dataclass
class Block30(MBusStruct):
    activationTimeTemperature : u16 = MemMapped.new(default=0,   metadata={'description': _('Tiempo que se activa las resistencias'),  'tags': [IODATA, TEMPERATURE]})

    C2H4MeasureRaw            : f32 = MemMapped.new(default=0-0, metadata={'description': _('Medida etileno'),       'tags': [RESERVED]}) # duplicated
    CO2MeasureRaw             : f32 = MemMapped.new(default=0-0, metadata={'description': _('Medida CO2'),           'tags': [RESERVED]}) # duplicated
    humidityInsideRaw         : f32 = MemMapped.new(default=0-0, metadata={'description': _('Humedad interior'),     'tags': [RESERVED]}) # duplicated
    humidityOutsideRaw        : f32 = MemMapped.new(default=0-0, metadata={'description': _('Humedad exterior'),     'tags': [RESERVED]}) # duplicated
    temperatureInsideRaw      : f32 = MemMapped.new(default=0-0, metadata={'description': _('Temperatura interior'), 'tags': [RESERVED]}) # duplicated
    temperatureOutsideRaw     : f32 = MemMapped.new(default=0-0, metadata={'description': _('Temperatura exterior'), 'tags': [RESERVED]}) # duplicated

    totalPower                : f32 = MemMapped.new(default=0.0, metadata={'description': _('Potencia total de la instalación'),    'tags': [IODATA, TEMPERATURE]})
    maxTotalPower             : f32 = MemMapped.new(default=0.0, metadata={'description': _('Potencia total máxima de la cámara'), 'tags': [IODATA, TEMPERATURE]})
    ethyleneCorrector         : f32 = MemMapped.new(default=0.0, metadata={'description': _('Correcion sensor etileno'),           'tags': [IODATA, TEMPERATURE]})
