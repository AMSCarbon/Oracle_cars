import datetime

from django import forms

# Helper class for quickly and cleanly handling date input.
# Using a form instead of a serializer because I'm more validating form input
# than a model. Serializers expect a create and update method, which would
# have to be left empty, which suggests it's not the best class form this
# DRF uses end_time because that's what the model has, so this handles both
# cases. Should probably also make them mutually exclusive.
class TimeframeForm(forms.Form):
    start_time = forms.DateTimeField()
    duration = forms.DurationField(required=False)
    end_time = forms.DateTimeField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        if not (cleaned_data.get("duration") or cleaned_data.get("end_time")):
            raise forms.ValidationError("duration or end_time are required.")
        if cleaned_data.get("duration") and cleaned_data.get(
            "duration"
        ) < datetime.timedelta(seconds=0):
            raise forms.ValidationError("duration cannot be negative")
        if cleaned_data.get("end_time") and cleaned_data.get(
            "start_time"
        ) > cleaned_data.get("end_time"):
            raise forms.ValidationError("start_time cannot be after end_time.")

    @property
    def start(self):
        return self.cleaned_data["start_time"]

    @property
    def end(self):
        if self.cleaned_data.get("end_time"):
            return self.cleaned_data["end_time"]
        return self.cleaned_data["start_time"] + self.cleaned_data["duration"]
