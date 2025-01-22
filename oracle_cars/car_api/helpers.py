from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from functools import wraps

def DoesNotExist_to_404(fn):
    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ObjectDoesNotExist as e:
            return Response({"error": str(e)}, 404)
    return wrapped_fn


# Might be good to rename and switch the args around.
def fill_missing_form_data(new, original, exclusions=None):
    if exclusions is None:
        exclusions = ["id"]

    for exc in exclusions:
        if exc in new:
            del new[exc]

    original.update(new)
    return original