from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Car,  Branch
from ..serializers import CarSerializer, BranchSerializer
from ..utils import DoesNotExist_to_404, get_inventory_at_date


class BranchView(APIView):
    serializer_class = BranchSerializer

    def get(self, request, *args, **kwargs):
        """
        Get all :model:`car_api.models.Branch`s.
        """
        branches = Branch.objects.all()
        seralizer = BranchSerializer(branches, many=True)
        return Response(seralizer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a single :model:`car_api.models.Branch`.
        """
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class BranchDetailView(APIView):
    serializer_class = BranchSerializer

    @DoesNotExist_to_404
    def get(self, request, pk, *args, **kwargs):
        """
        Display a single :model:`car_api.models.Branch`.
        """
        branch = Branch.objects.get(pk=pk)
        seralizer = BranchSerializer(branch)
        return Response(seralizer.data)

    @DoesNotExist_to_404
    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a single :model:`car_api.models.Branch`.
        """
        branch = Branch.objects.get(pk=pk)
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BranchInventoryView(APIView):
    @DoesNotExist_to_404
    def get(self, request, pk, *args, **kwargs):
        """
        Get a list of :model:`car_api.models.Car`s that are currently assigned
        to this :model:`car_api.models.Branch`.
        """
        Branch.objects.get(pk=pk)  # For 404
        cars_in_branch = Car.objects.filter(branch=pk)
        seralizer = CarSerializer(cars_in_branch, many=True)
        return Response(seralizer.data)

    @DoesNotExist_to_404
    def post(self, request, pk, *args, **kwargs):
        """
        Get a list of :model:`car_api.models.Car`s that will be at this
        :model:`car_api.models.Branch` at a given point of time.

        POST parameters:
        POST['at_time'] : The time for which we determine which cars would be
        present at our  :model:`car_api.models.Branch` .
        """
        branch = Branch.objects.get(pk=pk)
        cutoff = parse_datetime(request.data["at_time"])

        if not cutoff:
            return Response({"error": "valid 'at_time' value is required."})

        available_cars = get_inventory_at_date(branch, cutoff)
        serializer = CarSerializer(available_cars, many=True)
        if available_cars:
            return Response(serializer.data, status.HTTP_200_OK)
        return Response({"error": "No cars available for this time."}, status.HTTP_400_BAD_REQUEST)
