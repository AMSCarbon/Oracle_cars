from django import forms
import datetime

# Helper class for quickly and cleanly handling date input.
# Using a form instead of a serializer because I'm more validating form input
# than a model. Serializers expect a create and update method, which would
# have to be left empty, which suggests it's not the best class form this
class TimeframeForm(forms.Form):
    start_time = forms.DateTimeField()
    duration = forms.DurationField()

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('duration') < datetime.timedelta(seconds=0):
            raise forms.ValidationError("Duration cannot be negative")

    @property
    def start(self):
        return self.cleaned_data["start_time"]

    @property
    def end(self):
        return self.cleaned_data["start_time"] + self.cleaned_data["duration"]

