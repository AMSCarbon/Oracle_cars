from django.test import TransactionTestCase
from rest_framework.test import APIClient
from unittest.mock import patch

from . import DEFAULT_NOW
from ..models import Car, Schedule, Branch


@patch("car_api.utils.now", return_value=DEFAULT_NOW)
class BranchInventoryAPITests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.b1 = Branch.objects.create(name="Prague")
        self.b2 = Branch.objects.create(name="Prague")

        self.c1 = Car.objects.create(id="C1", make="test_make", model="test_model", branch=self.b1)
        self.c2 = Car.objects.create(id="C2", make="test_make", model="test_model", branch=self.b1)
        self.c3 = Car.objects.create(id="C3", make="test_make", model="test_model", branch=self.b2)

        self.s1 = Schedule.objects.create(start_time="2025-02-01 00:00:00",
                                          end_time="2025-02-05 00:00:00",
                                          car_id=self.c2,
                                          origin_branch=self.b1,
                                          destination_branch=self.b2)
        # Create some schedules to move cars about.
        self.client = APIClient()

    def test_get_inventory(self, mock_now):
        expected = [{'id': 'C1', 'make': 'test_make', 'model': "test_model", "branch": 1},
                    {'id': 'C2', 'make': 'test_make', 'model': "test_model", "branch": 1}]

        response = self.client.get("/api/branches/1/inventory")

        self.assertListEqual(expected, response.data)

    def test_post_inventory(self, mock_now):
        expected_b1 = [{'id': 'C1', 'make': 'test_make', 'model': "test_model",
                     "branch": 1}]
        expected_b2 = [
            {'id': 'C3', 'make': 'test_make', 'model': 'test_model', 'branch': 2},
            {'id': 'C2', 'make': 'test_make', 'model': 'test_model', 'branch': 1}
        ]

        b1_response = self.client.post("/api/branches/1/inventory", {"at_time": "2025-02-09"}, format='json')
        b2_response = self.client.post("/api/branches/2/inventory", {"at_time": "2025-02-09"}, format='json')

        self.assertListEqual(expected_b1, b1_response.data)
        self.assertListEqual(expected_b2, b2_response.data)

