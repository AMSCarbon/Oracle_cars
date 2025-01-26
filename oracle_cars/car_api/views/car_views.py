from django.forms.models import model_to_dict
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Car
from ..serializers import CarSerializer
from ..utils import DoesNotExist_to_404, update_model_from_form


class CarView(APIView):
    serializer_class = CarSerializer

    def get(self, request, *args, **kwargs):
        """
        Display all :model:`car_api.models.Car`s.
        """
        cars = Car.objects.all()
        seralizer = CarSerializer(cars, many=True)
        return Response(seralizer.data)

    def post(self, request, *args, **kwargs):
        """
        Create a single :model:`car_api.models.Car`.
        """
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CarDetailView(APIView):
    serializer_class = CarSerializer

    @DoesNotExist_to_404
    def get(self, request, pk, *args, **kwargs):
        """
        Display a single :model:`car_api.models.Car` based on ID.
        """
        car = Car.objects.get(pk=pk)
        seralizer = CarSerializer(car)
        return Response(seralizer.data)

    @DoesNotExist_to_404
    def put(self, request, pk, *args, **kwargs):
        """
        Update a :model:`car_api.models.Car`'s data.
        """
        car = Car.objects.get(pk=pk)
        updated_data = update_model_from_form(model_to_dict(car), request.data)
        serializer = CarSerializer(car, data=updated_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    @DoesNotExist_to_404
    def delete(self, request, pk, *args, **kwargs):
        """
        Delete a single :model:`car_api.models.Car` based on ID.
        """
        car = Car.objects.get(pk=pk)
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

