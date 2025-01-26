from django.utils.dateparse import parse_datetime

#A fair few tests rely on seeing which schedules are in the future. We mock
# them to make the testing consistent.
DEFAULT_NOW = parse_datetime("2025-01-25 00:00:00")
