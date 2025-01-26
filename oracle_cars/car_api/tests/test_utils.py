from django.test import TestCase
from django.utils.dateparse import parse_datetime
from unittest.mock import patch

from . import DEFAULT_NOW
from ..models import Car, Schedule, Branch
from ..utils import get_inventory_at_date, get_free_car_ids


@patch("car_api.utils.now", return_value=DEFAULT_NOW)
class LibTest(TestCase):
    def setUp(self):
        self.b1 = Branch.objects.create(name="Prague")
        self.b2 = Branch.objects.create(name="Brno")

        self.c1 = Car.objects.create(id="C1", make="test_make",
                                     model="test_model", branch=self.b1)
        self.c2 = Car.objects.create(id="C2", make="test_make",
                                     model="test_model", branch=self.b1)
        self.c3 = Car.objects.create(id="C3", make="test_make",
                                     model="test_model", branch=self.b1)

        self.s1 = Schedule.objects.create(start_time="2025-02-02 00:00:00",
                                          end_time="2025-02-03 00:00:00",
                                          car_id=self.c1,
                                          origin_branch=self.b1,
                                          destination_branch=self.b1)
        self.s2 = Schedule.objects.create(start_time="2025-02-04 00:00:00",
                                          end_time="2025-02-05 00:00:00",
                                          car_id=self.c2,
                                          origin_branch=self.b1,
                                          destination_branch=self.b2)

    def test_get_inventory_basic(self, mock_now):
        expected_inventory = [self.c1, self.c2, self.c3]

        # This date is before any schedule, so we expect all cars
        inventory = get_inventory_at_date(self.b1, parse_datetime("2025-01-05 00:00:00"))

        self.assertListEqual(expected_inventory, inventory)

    def test_get_inventory_empty(self, mock_now):
        expected_inventory = []

        # This date is before any schedule, no cars yet
        inventory = get_inventory_at_date(self.b2, parse_datetime("2025-01-05 00:00:00"))

        self.assertListEqual(expected_inventory, inventory)

    def test_get_inventory_round_trip(self, mock_now):
        # One trip has happened, from prague back to prague
        expected_inventory = [self.c1, self.c2, self.c3]

        inventory = get_inventory_at_date(self.b1, parse_datetime("2025-02-03 05:00:00"))

        self.assertListEqual(expected_inventory, inventory)

    def test_get_inventory_halfway_end(self, mock_now):
        # When the time request intersects with a schedule.
        # the car should show up in neither inventory.
        expected_b1_inventory = [self.c1, self.c3]
        expected_b2_inventory = []

        b1_inventory = get_inventory_at_date(self.b1, parse_datetime("2025-02-04 05:00:00"))
        b2_inventory = get_inventory_at_date(self.b2, parse_datetime("2025-02-04 05:00:00"))

        self.assertListEqual(expected_b1_inventory, b1_inventory)
        self.assertListEqual(expected_b2_inventory, b2_inventory)

    def test_get_free_cars_normal(self, mock_now):
        expected_available = [self.c1.id, self.c2.id, self.c3.id]

        #No schedules, no relocatison
        available = get_free_car_ids(self.b1, parse_datetime("2025-01-05 00:00:00"), parse_datetime("2025-01-06 00:00:00"))

        self.assertListEqual(expected_available, available)


    def test_get_free_cars_none_free(self, mock_now):
        expected_available = []

        #No schedules, no relocatison
        available = get_free_car_ids(self.b2, parse_datetime("2025-01-05 00:00:00"), parse_datetime("2025-01-06 00:00:00"))

        self.assertListEqual(expected_available, available)

    def test_get_free_cars_overlapping_schedules(self, mock_now):
        # Both c1 and c2 have schedules at this time. only c3 is available

        expected_available = [self.c3.id]

        available = get_free_car_ids(self.b1, parse_datetime("2025-02-02 00:00:00"), parse_datetime("2025-02-06 00:00:00"))

        self.assertListEqual(expected_available, available)