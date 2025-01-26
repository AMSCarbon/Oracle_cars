from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Schedule, Branch
from ..serializers import ScheduleSerializer
from ..forms import TimeframeForm
from ..utils import get_free_car_ids, DoesNotExist_to_404

class ScheduleView(APIView):
    serializer_class = ScheduleSerializer

    def get(self, request, *args, **kwargs):
        """
        Display all :model:`car_api.models.Schedule`s.
        """
        schedules = Schedule.objects.all()
        seralizer = ScheduleSerializer(schedules, many=True)
        return Response(seralizer.data)

    def post(self, request, *args, **kwargs):
        """
        Create and validate a single :model:`car_api.models.Schedule`.
        """
        # mutable copy of the post data
        fill_data = request.data.copy()
        tff = TimeframeForm(request.data)
        if not tff.is_valid():
            return Response(
                {"error": "timeframe could not be parsed properly."},
                status.HTTP_400_BAD_REQUEST)
        fill_data["end_time"] = tff.end

        # Move this into a function and raise errors if it fails.
        Branch.objects.get(pk=request.data["origin_branch"])  # trigger 404
        available_cars = get_free_car_ids(request.data["origin_branch"], tff.start, tff.end)

        if not available_cars:
            return Response(
                {"error": "No cars available for this time frame."},
                status.HTTP_400_BAD_REQUEST)
        # If the user supplied a car ID, check if it's free.
        if request.data.get("car_id") and request.data.get("car_id") not in available_cars:
            return Response({"error": "Requested car is not available for this time frame."},
                            status.HTTP_400_BAD_REQUEST)
        # we've got cars but haven't requested a specific one
        elif not request.data.get("car_id"):
            # No car provided, just use the first one in our list.
            fill_data["car_id"] = available_cars[0]
        serializer = ScheduleSerializer(data=fill_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ScheduleDetailView(APIView):
    serializer_class = ScheduleSerializer

    @DoesNotExist_to_404
    def get(self, request, pk, *args, **kwargs):
        """
        Display a :model:`car_api.models.Schedule`.
        """
        schedules = Schedule.objects.get(pk=pk)
        seralizer = ScheduleSerializer(schedules)
        return Response(seralizer.data)
