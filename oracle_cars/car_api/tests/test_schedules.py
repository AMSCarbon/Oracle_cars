from datetime import datetime

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from unittest.mock import patch

from . import DEFAULT_NOW
from ..models import Car, Schedule, Branch


class ScheduleObjectTests(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Prague")
        self.c1 = Car.objects.create(id="C1", make="Honda", model="Accord", branch=self.branch)
        self.c2 = Car.objects.create(id="C2", make="Honda", model="Accord", branch=self.branch)
        self.client = APIClient()

    def test_basic_schedule(self):
        expected_start = datetime(year=2025, month=2, day=2)
        expected_end = datetime(year=2025, month=2, day=7)

        s = Schedule.objects.create(start_time="2025-02-02 00:00:00",
                                    end_time="2025-02-07 00:00:00",
                                    car_id=self.c1,
                                    origin_branch=self.branch,
                                    destination_branch=self.branch)
        s.full_clean()

        self.assertEqual(s.start_time, expected_start)
        self.assertEqual(s.end_time, expected_end)

    def test_schedule_bad_times(self):
        s = Schedule.objects.create(start_time="2025-02-05 00:00:00",
                                    end_time="2025-02-02 00:00:00",
                                    car_id=self.c1,
                                    origin_branch=self.branch,
                                    destination_branch=self.branch)
        with self.assertRaises(ValidationError):
            s.full_clean()


class ScheduleAPITests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.b1 = Branch.objects.create(name="Prague")
        self.b2 = Branch.objects.create(name="Brno")
        self.b3 = Branch.objects.create(name="Ostrava")

        self.c1 = Car.objects.create(id="C1", make="Honda", model="Accord", branch=self.b1)
        self.c2 = Car.objects.create(id="C2", make="Ford", model="Falcon", branch=self.b1)

        self.s1 = Schedule.objects.create(start_time="2025-02-02 00:00:00",
                                          end_time="2025-02-07 00:00:00",
                                          car_id=self.c1, origin_branch=self.b1,
                                          destination_branch=self.b1)
        self.s2 = Schedule.objects.create(start_time="2025-02-04 00:00:00",
                                          end_time="2025-02-07 00:00:00",
                                          car_id=self.c2, origin_branch=self.b1,
                                          destination_branch=self.b1)
        self.s3 = Schedule.objects.create(start_time="2025-11-29 00:00:00",
                                          end_time="2025-12-01 00:00:00",
                                          car_id=self.c2, origin_branch=self.b1,
                                          destination_branch=self.b2)
        self.client = APIClient()


class ScheduleGetTests(ScheduleAPITests):
    def test_get_all_schedules(self):
        expected_data = [{'id': 1, 'start_time': '2025-02-02T00:00:00',
                          'end_time': '2025-02-07T00:00:00', 'car_id': 'C1',
                          "origin_branch": 1, "destination_branch": 1},
                         {'id': 2, 'start_time': '2025-02-04T00:00:00',
                          'end_time': '2025-02-07T00:00:00', 'car_id': 'C2',
                          "origin_branch": 1, "destination_branch": 1},
                         {'id': 3, 'start_time': '2025-11-29T00:00:00',
                          'end_time': '2025-12-01T00:00:00', 'car_id': 'C2',
                          "origin_branch": 1, "destination_branch": 2}
                         ]

        response = self.client.get('/api/schedules/', format='json')

        self.assertListEqual(response.data, expected_data)

    def test_get_specific_schedule(self):
        expected_data = {'id': 1, 'start_time': '2025-02-02T00:00:00',
                         'end_time': '2025-02-07T00:00:00', 'car_id': 'C1',
                         "origin_branch": 1, "destination_branch": 1}

        response = self.client.get('/api/schedules/1/', format='json')

        self.assertEqual(response.data, expected_data)


@patch("car_api.utils.now", return_value=DEFAULT_NOW)
class SchedulePostTests(ScheduleAPITests):
    def test_post_basic(self, mock_now):
        data = {'start_time': '2025-01-05T00:00:00',
                'duration': '05:00:00', 'car_id': 'C1', "origin_branch": self.b1.id,
                "destination_branch": self.b1.id}
        expected_data = {'id': 4, 'start_time': '2025-01-05T00:00:00',
                         'end_time': '2025-01-05T05:00:00', 'car_id': 'C1',
                         "origin_branch": self.b1.id, "destination_branch": self.b1.id}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')
        self.assertEqual(response.data, expected_data)

    def test_post_auto_assign_car(self, mock_now):
        data = {'start_time': '2025-11-29 00:00:00',
                'duration': '24:00:00', "origin_branch": 1, "destination_branch": 1}
        expected_data = {'id': 4, 'start_time': '2025-11-29T00:00:00',
                         'end_time': '2025-11-30T00:00:00', 'car_id': 'C1',
                         "origin_branch": 1, "destination_branch": 1}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')
        self.assertEqual(response.data, expected_data)

    def test_post_requested_car_unavailable(self, mock_now):
        # C1 is in use by s1, but C2 is available.
        data = {'start_time': '2025-02-02T00:00:00',
                'duration': '24:00:00', 'car_id': 'C1',
                "origin_branch": "1", "destination_branch": "1"}

        expected_response = {
            'error': 'Requested car is not available for this time frame.'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_post_no_cars_available(self, mock_now):
        data = {'start_time': '2025-02-02 00:00:00',
                'duration': '24:00:00',
                "origin_branch": "3", "destination_branch": "1"
                }

        expected_response = {'error': 'No cars available for this time frame.'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_post_bad_start_time(self, mock_now):
        data = {'start_time': 'Not a datetime',
                'duration': '24:00:00',
                "origin_branch": "1", "destination_branch": "1"}

        expected_response = {
            'error': 'timeframe could not be parsed properly.'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_post_bad_duration(self, mock_now):
        data = {'start_time': '2025-02-02 00:00:00', 'duration': '-24:00:00',
                "origin_branch": "1", "destination_branch": "1"
                }

        expected_response = {
            'error': 'timeframe could not be parsed properly.'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)
