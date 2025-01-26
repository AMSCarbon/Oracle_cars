from django.test import TestCase, TransactionTestCase
from ..models import Car, Branch
from rest_framework.test import APIClient

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.exceptions import ErrorDetail


class CarObjectTests(TestCase):
    def setUp(self) -> None:
        self.branch = Branch.objects.create(name="Prague")

    def test_car_id_validator(self):
        car = Car(id="NotValid", make="Honda", model="accord", branch=self.branch)
        expected_msg = "{'id': ['Car ID must start with C.']}"

        with self.assertRaises(ValidationError) as context:
            car.clean_fields()

        self.assertEqual(expected_msg, str(context.exception))

    def test_car_id_unique(self):
        # This message might be different across DB types.
        expected_msg = "UNIQUE constraint failed: car_api_car.id"

        with self.assertRaises(IntegrityError) as context:
            Car.objects.create(id="C1996", make="Honda", model="accord", branch=self.branch)
            Car.objects.create(id="C1996", make="Honda", model="accord",  branch=self.branch)

        self.assertEqual(expected_msg, str(context.exception))

    def test_car_requires_make(self):
        car = Car(id="C2003", make="", model="Falcon",  branch=self.branch)
        expected_msg = "{'make': ['This field cannot be blank.']}"

        with self.assertRaises(ValidationError) as context:
            car.clean_fields()
        self.assertEqual(expected_msg, str(context.exception))

    def test_car_requires_model(self):
        car = Car(id="C2003", make="Honda", model="", branch=self.branch)
        expected_msg = "{'model': ['This field cannot be blank.']}"

        with self.assertRaises(ValidationError) as context:
            car.clean_fields()

        self.assertEqual(expected_msg, str(context.exception))


class CarAPITests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.branch = Branch.objects.create(name="Prague")
        Car.objects.create(id="C1996", make="Honda", model="Accord", branch=self.branch)
        Car.objects.create(id="C2025", make="Ford", model="Falcon", branch=self.branch)
        self.client = APIClient()


class CarGetTests(CarAPITests):
    def test_get_all_cars(self):
        expected_data = [{'id': 'C1996', 'make': 'Honda', 'model': "Accord", "branch":1},
                         {'id': 'C2025', 'make': 'Ford', 'model': "Falcon", "branch":1}]

        response = self.client.get('/api/cars/', format='json')

        self.assertListEqual(response.data, expected_data)

    def test_get_specific_car(self):
        expected_data = {'id': 'C1996', 'make': 'Honda', 'model': "Accord", "branch":1}

        response = self.client.get('/api/cars/C1996/', format='json')

        self.assertEqual(response.data, expected_data)


class CarPostTests(CarAPITests):
    def test_create_new_car(self):
        car_data = {'id': 'C1981', 'make': 'DMC', 'model': "DeLorean", "branch":1}

        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, car_data)

    def test_create_new_car_duplicate_ID(self):
        car_data = {'id': 'C2025', 'make': 'test', 'model': "test", "branch":1}
        expected_error = {'id': [
            ErrorDetail(string='car with this id already exists.',
                        code='unique')]}
        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_error)

    def test_create_new_car_bad_ID(self):
        car_data = {'id': 'ThisDoesntStartwithC', 'make': 'test',
                    'model': "test", "branch":1}
        expected_error = {'id': [
            ErrorDetail(string='Car ID must start with C.', code='invalid')]}
        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_error)

    def test_create_new_car_missing_field(self):
        car_data = {'id': 'C10000', 'make': 'test', 'branch': 1}
        expected_error = {'model': [
            ErrorDetail(string='This field is required.', code='required')]}
        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, expected_error)

    def test_create_new_car_additional_field(self):
        car_data = {'id': 'C10001', 'make': 'test', 'model': "test", "branch":1,
                    "meat_type": "chicken"}
        expected = {'id': 'C10001', 'make': 'test', 'model': "test", "branch":1}

        response = self.client.post('/api/cars/', car_data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, expected)


class CarPutTests(CarAPITests):
    def test_update_runs_normally(self):
        car_data = {'make': 'test'}
        expected_data = {'id': 'C1996', 'make': 'test', 'model': "Accord", "branch":1}

        response = self.client.put('/api/cars/C1996/', car_data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_data)

    def test_update_ignores_id_change(self):
        car_data = {'id': 'C1997', 'model': "test"}
        expected_data = {'id': 'C1996', 'make': 'Honda', 'model': "test", "branch":1}

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
