import pytz
from django.conf import settings
from django.utils import timezone

utc_now = timezone.now()


def time_now():
    return utc_now.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%b %d, %Y %I:%M %p")
