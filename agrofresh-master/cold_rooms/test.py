from django.test import TestCase
from cold_rooms.models import ColdRoom


class ColdRoomTestCase(TestCase):
    def test_cold_room_can_be_deleted(self):
        cold_room = ColdRoom.objects.create(name='ColdRoom', description='A Cold Room')
        cold_room.delete()