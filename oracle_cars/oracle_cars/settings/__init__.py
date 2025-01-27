import os

if os.environ.get("CAR_API_DEPLOYMENT") == "PROD":
    from .prod import *
else:
    from .local import *
