from django.db import models

from django.core.exceptions import ValidationError


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
    id = models.CharField(primary_key=True, validators=[validate_car_id], max_length=100)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)


class Schedule(models.Model):
    # This works for our case since we have one car per Schedule. If we had
    # several cars, we might want an extra table.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    car_id = models.ForeignKey(Car, on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        if self.start_time > self.end_time:
            raise ValidationError("start_time cannot be before end_time.")
