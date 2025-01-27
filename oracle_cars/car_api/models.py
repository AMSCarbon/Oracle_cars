from django.db import models
from django.core.exceptions import ValidationError


# Why not just make this a CharField? Because a modeled object is more
# rigorous and branches might be used for other things down the line, having
# something in place now makes it easier than dealing with another migration.
class Branch(models.Model):
    name = models.CharField(max_length=50)


def validate_car_id(new_id):
    try:
        # Car IDs should start with C. I can imagine a scenario where we
        # introduce different vehicle types, but might have some opperations
        # where we don't care about the specific types. Removing the C might lead to overlapping IDs.
        if not new_id.startswith("C"):
            raise ValidationError("Car ID must start with C.")
        elif not new_id[1:].isnumeric():
            raise ValidationError("Car ID should follow the pattern C<number>.")
        else:
            return new_id
    except AttributeError:
        ValidationError("Car ID should be a string value.")


class Car(models.Model):
    id = models.CharField(
        primary_key=True, validators=[validate_car_id], max_length=100
    )
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    # Make a required home branch and optional current branch, which would be
    # set to None when the schedule starts.
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)


class Schedule(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    car_id = models.ForeignKey(Car, on_delete=models.CASCADE)
    origin_branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="+"
    )
    destination_branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="+"
    )

    def clean(self):
        super().clean()
        if self.start_time > self.end_time:
            raise ValidationError("start_time cannot be before end_time.")
