from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from datetime import datetime
from django.db.models import Q

from .models import Car, Schedule

# Mix of utility functions and business logic. I'd split this into two files if
# it got longer over time.


def now():
    """Utility function for unittest mocking."""
    return datetime.now()


def get_free_car_ids(origin, start_time, end_time):
    """
    Given a branch and a start and end time, return a list which cars are
    available for booking. Finds cars that would be at the start location
    given the start time, then exclude those that already have a booking
    within the  time frame
    """
    available_at_start_loc = [c.id for c in get_inventory_at_date(origin, start_time)]

    booked_cars = (
        Schedule.objects.exclude(start_time__gt=end_time)
        .exclude(end_time__lt=start_time)
        .values("car_id")
    )

    free_cars = Car.objects.exclude(id__in=booked_cars).filter(
        id__in=available_at_start_loc
    )

    # Doesn't account for follow up schedules and transfer time between
    # branches.
    # for cars in free_cars:
    # if car has no more schedules or closest schedule.orgin_branch = origin:
    # return car
    # all cars have schedules, none start here
    # for car in free_cars:
    # if end_time + transfer_duration > closest schedule
    # remove car from free cars
    return [c.id for c in free_cars]


def get_inventory_at_date(branch, cutoff_time):
    """
    Given a cutoff time, determine which cars would be assigned to
    this branch based on all the relevant schedules. This algorithm is a bit
    bruteforce-y, as it considers all schedules.
    """
    current_inventory = list(Car.objects.filter(branch=branch))
    start_time = now()

    # Get all the schedules relevant to us. Schedules may be in progress.
    # SELECT * from Schedules WHERE end_time > now AND start_time < cutoff_time
    #     AND (origin_branch = branch OR destination_branch = branch)
    try:
        schedules = Schedule.objects.filter(
            Q(end_time__gt=start_time),
            Q(start_time__lt=cutoff_time),
            Q(origin_branch=branch) | Q(destination_branch=branch),
        ).order_by("-end_time")
    except ObjectDoesNotExist:
        schedules = []

    for s in list(schedules):
        # ends at our branch. we don't care about the origin.
        if (
            s.destination_branch == branch
            and s.car_id not in current_inventory
            and s.end_time < cutoff_time
        ):
            current_inventory.append(s.car_id)
        # if the start branch is ours, the car shooould be there.
        elif (
            s.origin_branch == branch
            and s.destination_branch != branch
            and s.car_id in current_inventory
        ):
            current_inventory.remove(s.car_id)

    return list(current_inventory)


def DoesNotExist_to_404(fn):
    """
    Helper wrapper to automatically catch DoesNotExist exceptions and return
    a 404 error.
    """

    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ObjectDoesNotExist as e:
            return Response({"error": str(e)}, 404)

    return wrapped_fn


def update_model_from_form(original, new, exclusions=None):
    """
    Given some dictionary with old data, update with new data, except for
    a list of exclusions.
    """
    if exclusions is None:
        exclusions = ["id"]

    for exc in exclusions:
        if exc in new:
            del new[exc]

    original.update(new)
    return original
