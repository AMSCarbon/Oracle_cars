from django.forms.models import model_to_dict

from .models import Car, Schedule
from .serializers import CarSerializer, ScheduleSerializer
from .forms import TimeframeForm
from .lib import get_free_car_ids
from .helpers import DoesNotExist_to_404, fill_missing_form_data

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class CarView(APIView):
    serializer_class = CarSerializer

    def get(self, request, *args, **kwargs):
        cars = Car.objects.all()
        seralizer = CarSerializer(cars, many=True)
        return Response(seralizer.data)

    def post(self, request,  *args, **kwargs):
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class CarDetailView(APIView):
    serializer_class = CarSerializer

    @DoesNotExist_to_404
    def get(self, request, pk, *args, **kwargs):
        car = Car.objects.get(pk=pk)
        seralizer = CarSerializer(car)
        return Response(seralizer.data)

    @DoesNotExist_to_404
    def put(self, request, pk,  *args, **kwargs):
        car = Car.objects.get(pk=pk)
        new_data = fill_missing_form_data(request.data, model_to_dict(car))
        serializer = CarSerializer(car, data=new_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    @DoesNotExist_to_404
    def delete(self, request, pk,  *args, **kwargs):
        car = Car.objects.get(pk=pk)
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ScheduleView(APIView):
    serializer_class = ScheduleSerializer

    def get(self, request, *args, **kwargs):
        schedules = Schedule.objects.all()
        seralizer = ScheduleSerializer(schedules, many=True)
        return Response(seralizer.data)

    def post(self, request,  *args, **kwargs):
        tff = TimeframeForm(request.data)
        if not tff.is_valid():
            return Response({"error": "start_time or duration could not be parsed properly."}, status.HTTP_400_BAD_REQUEST)
        request.data["end_time"] = tff.end
        # Move this into a function and raise errors if it fails.
        available_cars = get_free_car_ids(tff.start, tff.end)
        if not available_cars:
            return Response({"error": "No cars available for this time frame."}, status.HTTP_400_BAD_REQUEST)
        # If the user supplied a car ID, check if it's free.
        if request.data.get("car_id") and request.data.get("car_id") not in available_cars:
            return Response({"error": "Requested car is not available for this time frame."},status.HTTP_400_BAD_REQUEST )
        else:
            # No car provided, just use the first one in our list.
            request.data["car_id"] = available_cars[0]

        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ScheduleDetailView(APIView):
    serializer_class = ScheduleSerializer

    @DoesNotExist_to_404
    def get(self, request, pk,  *args, **kwargs):
        schedules = Schedule.objects.get(pk=pk)
        seralizer = ScheduleSerializer(schedules)
        return Response(seralizer.data)
