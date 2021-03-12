from django.conf import settings
from django.db import connection
from django.forms.models import model_to_dict
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from cold_rooms.models import ColdRoom
from core.models import Typed
from . import models

import pytz
tz = getattr(settings, 'TIME_ZONE', None)
tzinfo = pytz.timezone(tz)
t0 = timezone.datetime(2020, 11, 18, 8, 0, 0, tzinfo=tzinfo)


class DownsampledFuncsTestCase(TestCase):
    # TODO DRY
    def test_downsampled_float_data(self):
        now = timezone.now()
        cold_room = ColdRoom.objects.create(name='ColdRoom', description='A Cold Room')
        measurement = models.Measurement.objects.create(
            name='Measurement',
            type=Typed.Type.FLOAT,
        )
        models.FloatData.objects.bulk_create(
            models.FloatData(
                ts=now - n*timedelta(minutes=1),
                cold_room=cold_room,
                measurement=measurement,
                value=(n % 100) * 1.0,
            )
            for n in range(10000)
        )
        points = 100
        model = models.measurements.FloatDataDownsampled
        model.create_or_replace()
        qs = model.objects.all().table_function(
            from_ts=now,
            to_ts=now - 2*timedelta(days=1),
            cold_room_id=cold_room.pk,
            measurement_id=measurement.pk,
            points=points,
            # sample_time=timedelta(seconds=0.5),
        )
        sql = str(qs.query)
        self.assertIsInstance(sql, str)
        self.assertNotIn("ON", sql)
        self.assertNotIn("INNER JOIN", sql)
        results = qs.all()
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        self.assertEquals(len(results), points)

    def test_downsampled_int_data(self):
        now = timezone.now()
        cold_room = ColdRoom.objects.create(name='ColdRoom', description='A Cold Room')
        measurement = models.Measurement.objects.create(
            name='Measurement',
            type=Typed.Type.INT,
        )
        models.IntegerData.objects.bulk_create(
            models.IntegerData(
                ts=now - n*timedelta(minutes=1),
                cold_room=cold_room,
                measurement=measurement,
                value=(n % 100),
            )
            for n in range(10000)
        )
        points = 100
        model = models.measurements.IntegerDataDownsampled
        model.create_or_replace()
        qs = model.objects.all().table_function(
            from_ts=now,
            to_ts=now - 2*timedelta(days=1),
            cold_room_id=cold_room.pk,
            measurement_id=measurement.pk,
            points=points,
            # sample_time=timedelta(seconds=0.5),
        )
        sql = str(qs.query)
        self.assertIsInstance(sql, str)
        self.assertNotIn("ON", sql)
        self.assertNotIn("INNER JOIN", sql)
        results = qs.all()
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        self.assertEquals(len(results), points)

    def test_downsampled_form(self):
        params = {
            "from_ts": "2020-10-23T09:38:09.680Z",
            "to_ts": "2020-09-23T09:38:09.680Z",
            "cold_room_id": 1,
            "measurement_id": 35
        }
        form = models.MeasurementDataDownsampled.Form(params)
        self.assertTrue(form.is_valid())


class EventsTestCase(TestCase):
    def test_parameter_types(self):
        models.events.Parameter.update()
        unknown_type_params = models.events.Parameter.objects\
            .filter(type=Typed.Type.__empty__)
        self.assertFalse(unknown_type_params.exists())

    def test_event_save_on_value_change(self):
        data = dict(
            ts=timezone.now(),
            type='SampleEvent',
            meta={'a': 1, 'b': False, 'c': 'str'},
            value=1,
        )
        event = models.events.Event(**data)
        self.assertEquals(event.get_latest_value(), None)
        self.assertEquals(models.events.Event.objects.count(), 0)

        event = models.events.Event(**{ **data, 'ts': timezone.now(), 'value': 1 })
        event.save()
        self.assertEquals(event.get_latest_value(), 1)
        self.assertEquals(models.events.Event.objects.count(), 1)


        event = models.events.Event(**{ **data, 'ts': timezone.now(), 'value': 1 })
        event.save()
        self.assertEquals(event.get_latest_value(), 1)
        self.assertEquals(models.events.Event.objects.count(), 1)

        event = models.events.Event(**{ **data, 'ts': timezone.now(), 'value': 2 })
        event.save()
        self.assertEquals(event.get_latest_value(), 2)
        self.assertEquals(models.events.Event.objects.count(), 2)

        event = models.events.Event(**{ **data, 'ts': timezone.now(), 'value': 2 })
        self.assertEquals(event.get_latest_value(), 2)
        self.assertEquals(models.events.Event.objects.count(), 2)


class AlarmsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        alarm = models.events.Alarm.objects.create(id=1, name='Alarm1', enabled=True)

        cold_rooms = [
            ColdRoom.objects.create(id=1, name='ColdRoom 1', description='A Cold Room'),
            ColdRoom.objects.create(id=2, name='ColdRoom 2', description='Another Cold Room'),
        ]


        events = [
            models.events.AlarmEvent(
                ts=t0,
                cold_room=cold_rooms[0],
                alarm=alarm,
                value=True,
            ),
            models.events.AlarmEvent(
                ts=t0 + timedelta(seconds=2),
                cold_room=cold_rooms[1],
                alarm=alarm,
                value=True,
            ),
            models.events.AlarmEvent(
                ts=t0 + timedelta(seconds=10),
                cold_room=cold_rooms[0],
                alarm=alarm,
                value=False,
            ),
            models.events.AlarmEvent(
                ts=t0 + timedelta(seconds=12),
                cold_room=cold_rooms[1],
                alarm=alarm,
                value=False,
            ),
            models.events.AcknowledgeAlarmsEvent(
                ts=t0 + timedelta(seconds=15),
                cold_room=cold_rooms[1],
                user='admin',
            ),
            models.events.AlarmEvent(
                ts=t0 + timedelta(seconds=20),
                cold_room=cold_rooms[0],
                alarm=alarm,
                value=True,
            ),
            models.events.AlarmEvent(
                ts=t0 + timedelta(seconds=22),
                cold_room=cold_rooms[1],
                alarm=alarm,
                value=True,
            ),
            models.events.AcknowledgeAlarmsEvent(
                ts=t0 + timedelta(seconds=25),
                user='admin',
            ),
            models.events.AlarmEvent(
                ts=t0 + timedelta(seconds=30),
                cold_room=cold_rooms[0],
                alarm=alarm,
                value=False,
            ),
            models.events.AlarmEvent(
                ts=t0 + timedelta(seconds=32),
                cold_room=cold_rooms[1],
                alarm=alarm,
                value=False,
            ),
            models.events.AlarmEvent(
                ts=t0 + timedelta(seconds=40),
                cold_room=cold_rooms[0],
                alarm=alarm,
                value=True,
            ),
        ]

        for event in events:
            event.save()

    def test_get_annotated_alarms_detects_all_rising_edges(self):
        alarms = models.events.Event.alarms.get_annotated_alarms()
        self.assertEquals(len(alarms), 5, "Expected 5 alarms (rising edges)")

    # TODO test intermediate states
    # def test_get_annotated_alarms_ts_10s(self): pass
    # def test_get_annotated_alarms_ts_20s(self): pass
    # def test_get_annotated_alarms_ts_40s(self): pass

    def test_get_annotated_alarms(self):
        alarms = models.events.Event.alarms.get_annotated_alarms()

        self.assertEquals(len(alarms), 5, "Expected 5 alarms (rising edges)")
        self.assertEqual(alarms[0].ts, t0 + timedelta(seconds=40))
        self.assertEqual(alarms[1].ts, t0 + timedelta(seconds=22))
        self.assertEqual(alarms[2].ts, t0 + timedelta(seconds=20))
        self.assertEqual(alarms[3].ts, t0 + timedelta(seconds=2))
        self.assertEqual(alarms[4].ts, t0)

        self.assertEqual(alarms[0].meta.get('cold_room'), 1)
        self.assertEqual(alarms[1].meta.get('cold_room'), 2)
        self.assertEqual(alarms[2].meta.get('cold_room'), 1)
        self.assertEqual(alarms[3].meta.get('cold_room'), 2)
        self.assertEqual(alarms[4].meta.get('cold_room'), 1)

        self.assertEqual(alarms[0].ts_end, None)
        self.assertEqual(alarms[1].ts_end, t0 + timedelta(seconds=32))
        self.assertEqual(alarms[2].ts_end, t0 + timedelta(seconds=30))
        self.assertEqual(alarms[3].ts_end, t0 + timedelta(seconds=12))
        self.assertEqual(alarms[4].ts_end, t0 + timedelta(seconds=10))

        self.assertEqual(alarms[0].active, True)
        self.assertEqual(alarms[1].active, False)
        self.assertEqual(alarms[2].active, False)
        self.assertEqual(alarms[3].active, False)
        self.assertEqual(alarms[4].active, False)

        self.assertEqual(alarms[0].ts_ack, None)
        self.assertEqual(alarms[1].ts_ack, None)
        self.assertEqual(alarms[2].ts_ack, None)
        self.assertEqual(alarms[3].ts_ack, t0 + timedelta(seconds=15))
        self.assertEqual(alarms[4].ts_ack, t0 + timedelta(seconds=25))

        self.assertEqual(alarms[0].ack, False)
        self.assertEqual(alarms[1].ack, False)
        self.assertEqual(alarms[2].ack, False)
        self.assertEqual(alarms[3].ack, True)
        self.assertEqual(alarms[4].ack, True)

    def test_get_unacknowledged_alarms(self):
        not_ack_alarms = models.events.Event.alarms.get_unacknowledged_alarms()
        self.assertEquals(len(not_ack_alarms), 3, "Expected 2 unacknowledged alarms")


class ParamsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        params = [
            models.events.Parameter.objects.create(id=n, name=name, enabled=True)
            for n, name in enumerate([
                'workingMode',
                'refTemperature',
                'refHumidity',
                'highRefCO2',
                'lowRefCO2',
                'refC2H4',
            ])
        ]

        cold_rooms = [
            ColdRoom.objects.create(id=1, name='ColdRoom 1', description='A Cold Room'),
            ColdRoom.objects.create(id=2, name='ColdRoom 2', description='Another Cold Room'),
        ]

        events = [
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[0], value=True, ts=t0,
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[1], value=1, ts=t0 + timedelta(seconds=0.1),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[2], value=2, ts=t0 + timedelta(seconds=0.2),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[3], value=3, ts=t0 + timedelta(seconds=0.3),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[4], value=4, ts=t0 + timedelta(seconds=0.4),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[5], value=6, ts=t0 + timedelta(seconds=0.5),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[5], value=5, ts=t0 + timedelta(seconds=0.6),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[1], parameter=params[5], value=0, ts=t0 + timedelta(seconds=0.7),
            ),

            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[0], value=False, ts=t0 + timedelta(seconds=1),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[1], value=10, ts=t0 + timedelta(seconds=1.1),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[2], value=20, ts=t0 + timedelta(seconds=1.2),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[3], value=30, ts=t0 + timedelta(seconds=1.3),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[4], value=40, ts=t0 + timedelta(seconds=1.4),
            ),
            models.events.ParameterChangeEvent(
                cold_room=cold_rooms[0], parameter=params[5], value=50, ts=t0 + timedelta(seconds=1.5),
            ),
        ]

        for event in events:
            event.save()

    def test_get_latest_settings_returns_one_value_per_parameter(self):
        params = models.events.Event.params.get_latest_settings(1, False)
        self.assertEquals(len(params), 6, "Expected 6 param changes")

    # TODO test intermediate states
    # def test_get_latest_settings_ts_10s(self): pass
    # def test_get_latest_settings_ts_20s(self): pass
    # def test_get_latest_settings_ts_40s(self): pass

    def test_get_latest_settings(self):
        params = models.events.Event.params.get_latest_settings(1, True)
        self.assertEqual(params[0].value, True)
        self.assertEqual(params[1].value, 1)
        self.assertEqual(params[2].value, 2)
        self.assertEqual(params[3].value, 3)
        self.assertEqual(params[4].value, 4)
        self.assertEqual(params[5].value, 5)

        self.assertEqual(params[0].ts, t0 + timedelta(seconds=0))
        self.assertEqual(params[1].ts, t0 + timedelta(seconds=0.1))
        self.assertEqual(params[2].ts, t0 + timedelta(seconds=0.2))
        self.assertEqual(params[3].ts, t0 + timedelta(seconds=0.3))
        self.assertEqual(params[4].ts, t0 + timedelta(seconds=0.4))
        self.assertEqual(params[5].ts, t0 + timedelta(seconds=0.6))


        params = models.events.Event.params.get_latest_settings(1, False)
        self.assertEqual(params[0].value, False)
        self.assertEqual(params[1].value, 10)
        self.assertEqual(params[2].value, 20)
        self.assertEqual(params[3].value, 30)
        self.assertEqual(params[4].value, 40)
        self.assertEqual(params[5].value, 50)

        self.assertEqual(params[0].ts, t0 + timedelta(seconds=1))
        self.assertEqual(params[1].ts, t0 + timedelta(seconds=1.1))
        self.assertEqual(params[2].ts, t0 + timedelta(seconds=1.2))
        self.assertEqual(params[3].ts, t0 + timedelta(seconds=1.3))
        self.assertEqual(params[4].ts, t0 + timedelta(seconds=1.4))
        self.assertEqual(params[5].ts, t0 + timedelta(seconds=1.5))
