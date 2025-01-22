from django.test import TestCase, TransactionTestCase
from .models import Car, Schedule
from rest_framework.test import APIClient

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.exceptions import ErrorDetail

from datetime import datetime


class CarObjectTests(TestCase):
    def test_car_id_validator(self):
        car = Car(id="NotValid", make="Honda", model="accord")
        expected_msg = "{'id': ['Car ID must start with C.']}"

        with self.assertRaises(ValidationError) as context:
            car.clean_fields()

        self.assertEqual(expected_msg, str(context.exception))


    def test_car_id_unique(self):
        # This message might be different across DB types.
        expected_msg = "UNIQUE constraint failed: car_api_car.id"

        with self.assertRaises(IntegrityError) as context:
            Car.objects.create(id="C1996", make="Honda", model="accord")
            Car.objects.create(id="C1996", make="Honda", model="accord")

        self.assertEqual(expected_msg, str(context.exception))

    def test_car_requires_make(self):
        car = Car(id="C2003", make="", model="Falcon")
        expected_msg = "{'make': ['This field cannot be blank.']}"

        with self.assertRaises(ValidationError) as context:
            car.clean_fields()
        self.assertEqual(expected_msg, str(context.exception))

    def test_car_requires_model(self):
        car = Car(id="C2003", make="Honda", model="")
        expected_msg = "{'model': ['This field cannot be blank.']}"

        with self.assertRaises(ValidationError) as context:
            car.clean_fields()

        self.assertEqual(expected_msg, str(context.exception))


class CarAPITests(TransactionTestCase):
    def setUp(self):
        Car.objects.create(id="C1996", make="Honda", model="Accord")
        Car.objects.create(id="C2025", make="Ford", model="Falcon")
        self.client = APIClient()


class CarGetTests(CarAPITests):
    def test_get_all_cars(self):
        expected_data = [{'id': 'C1996', 'make': 'Honda', 'model': "Accord"},
                         {'id': 'C2025', 'make': 'Ford', 'model': "Falcon"}]
        response = self.client.get('/api/cars/', format='json')

        self.assertListEqual(response.data, expected_data)

    def test_get_specific_car(self):
        expected_data = {'id': 'C1996', 'make': 'Honda', 'model': "Accord"}

        response = self.client.get('/api/cars/C1996/', format='json')

        self.assertEqual(response.data, expected_data)


class CarPostTests(CarAPITests):
    def test_create_new_car(self):
        car_data = {'id': 'C1981', 'make': 'DMC', 'model': "DeLorean"}

        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, car_data)

    def test_create_new_car_duplicate_ID(self):
        car_data = {'id': 'C2025', 'make': 'test', 'model': "test"}
        expected_error = {'id': [
            ErrorDetail(string='car with this id already exists.',
                        code='unique')]}
        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_error)

    def test_create_new_car_bad_ID(self):
        car_data = {'id': 'ThisDoesntStartwithC', 'make': 'test',
                    'model': "test"}
        expected_error = {'id': [
            ErrorDetail(string='Car ID must start with C.', code='invalid')]}
        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_error)

    def test_create_new_car_missing_field(self):
        car_data = {'id': 'C10000', 'make': 'test'}
        expected_error = {'model': [
            ErrorDetail(string='This field is required.', code='required')]}
        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_error)

    def test_create_new_car_additional_field(self):
        car_data = {'id': 'C10001', 'make': 'test', 'model': "test",
                    "meat_type": "chicken"}
        expected = {'id': 'C10001', 'make': 'test', 'model': "test"}

        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, expected)


class CarPutTests(CarAPITests):
    def test_update_runs_normally(self):
        car_data = {'make': 'test'}
        expected_data = {'id': 'C1996', 'make': 'test', 'model': "Accord"}

        response = self.client.put('/api/cars/C1996/', car_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_update_ignores_id_change(self):
        car_data = {'id': 'C1997', 'model': "test"}
        expected_data = {'id': 'C1996', 'make': 'Honda', 'model': "test"}

        response = self.client.put('/api/cars/C1996/', car_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_404_when_id_not_found(self):
        car_data = {'make': 'test', 'model': "test"}

        response = self.client.put('/api/cars/C987654321/', car_data,
                                   format='json')

        self.assertEqual(response.status_code, 404)


class CarDeleteTests(CarAPITests):
    def test_delete_runs_normally(self):
        response = self.client.delete('/api/cars/C1996/', format='json')

        self.assertEqual(response.status_code, 204)

    def test_404_when_id_not_found(self):
        response = self.client.delete('/api/cars/C987654321/', format='json')

        self.assertEqual(response.status_code, 404)


class ScheduleObjectTests(TestCase):
    def setUp(self):
        self.c1 = Car.objects.create(id="C1", make="Honda", model="Accord")
        self.c2 = Car.objects.create(id="C2", make="Honda", model="Accord")
        self.client = APIClient()

    def test_basic_schedule(self):
        expected_start = datetime(year=2025, month=2, day=2)
        expected_end = datetime(year=2025, month=2, day=7)

        s = Schedule.objects.create(start_time="2025-02-02 00:00:00",
                                    end_time="2025-02-07 00:00:00",
                                    car_id=self.c1)
        s.full_clean()

        self.assertEqual(s.start_time, expected_start)
        self.assertEqual(s.end_time, expected_end)

    def test_schedule_bad_times(self):
        s = Schedule.objects.create(start_time="2025-02-05 00:00:00",
                                    end_time="2025-02-02 00:00:00",
                                    car_id=self.c1)
        with self.assertRaises(ValidationError):
            s.full_clean()


class ScheduleAPITests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.c1 = Car.objects.create(id="C1", make="Honda", model="Accord")
        self.c2 = Car.objects.create(id="C2", make="Ford", model="Falcon")
        self.s1 = Schedule.objects.create(start_time="2025-02-02 00:00:00",
                                          end_time="2025-02-07 00:00:00",
                                          car_id=self.c1)
        self.s2 = Schedule.objects.create(start_time="2025-02-02 00:00:00",
                                          end_time="2025-02-07 00:00:00",
                                          car_id=self.c2)
        self.s3 = Schedule.objects.create(start_time="2025-11-29 00:00:00",
                                          end_time="2025-12-01 00:00:00",
                                          car_id=self.c2)
        self.client = APIClient()


class ScheduleGetTests(ScheduleAPITests):
    def test_get_all_cars(self):
        expected_data = [{'id': 1, 'start_time': '2025-02-02T00:00:00Z',
                          'end_time': '2025-02-07T00:00:00Z', 'car_id': 'C1'},
                         {'id': 2, 'start_time': '2025-02-02T00:00:00Z',
                          'end_time': '2025-02-07T00:00:00Z', 'car_id': 'C2'},
                         {'id': 3, 'start_time': '2025-11-29T00:00:00Z',
                          'end_time': '2025-12-01T00:00:00Z', 'car_id': 'C2'}]

        response = self.client.get('/api/schedules/', format='json')

        self.assertListEqual(response.data, expected_data)

    def test_get_specific_schedule(self):
        expected_data = {'id': 1, 'start_time': '2025-02-02T00:00:00Z',
                         'end_time': '2025-02-07T00:00:00Z', 'car_id': 'C1'}

        response = self.client.get('/api/schedules/1/', format='json')

        self.assertEqual(response.data, expected_data)


class SchedulePostTests(ScheduleAPITests):
    def test_post_basic(self):
        data = {'start_time': '2025-03-05T00:00:00',
                'duration': '05:00:00', 'car_id': 'C1'}
        expected_data = {'id': 4, 'start_time': '2025-03-05T00:00:00Z',
                         'end_time': '2025-03-05T05:00:00Z', 'car_id': 'C1'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')
        self.assertEqual(response.data, expected_data)

    def test_post_auto_assign_car(self):
        data = {'start_time': '2025-11-29 00:00:00',
                'duration': '24:00:00'}
        expected_data = {'id': 4, 'start_time': '2025-11-29T00:00:00Z',
                         'end_time': '2025-11-30T00:00:00Z', 'car_id': 'C1'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')
        self.assertEqual(response.data, expected_data)

    def test_post_requested_car_unavailable(self):
        data = {'start_time': '2025-11-29 00:00:00',
                'duration': '24:00:00', 'car_id': 'C2'}

        expected_response = {
            'error': 'Requested car is not available for this time frame.'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_post_no_cars_available(self):
        data = {'start_time': '2025-02-02 00:00:00',
                'duration': '24:00:00'}

        expected_response = {'error': 'No cars available for this time frame.'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_post_bad_start_time(self):
        data = {'start_time': 'Not a datetime',
                'duration': '24:00:00'}

        expected_response = {
            'error': 'start_time or duration could not be parsed properly.'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)

    def test_post_bad_duration(self):
        data = {'start_time': '2025-02-02 00:00:00',
                'duration': '-24:00:00'}

        expected_response = {
            'error': 'start_time or duration could not be parsed properly.'}

        response = self.client.post('/api/schedules/', data=data,
                                    format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response)
