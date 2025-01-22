#Business logic.

from .models import Car, Schedule

def get_free_car_ids(start, end):
    # Given a start and end time, determine which cars are available.
    booked_cars = Schedule.objects.exclude(start_time__gt=end).exclude(
        end_time__lt=start).values("car_id")
    free_cars = Car.objects.exclude(id__in=booked_cars)
    return [c.id for c in free_cars]
