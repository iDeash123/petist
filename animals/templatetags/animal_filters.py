from django import template
from django.utils import timezone
import datetime

register = template.Library()


@register.filter
def age(birth_date):
    if not birth_date:
        return ""


    start_of_day = datetime.datetime.combine(birth_date, datetime.time.min)
    if timezone.is_aware(timezone.now()):
        start_of_day = timezone.make_aware(start_of_day)

    now = timezone.now()
    delta = now - start_of_day

    if delta.total_seconds() < 0:
        return "Not born yet"

    hours = int(delta.total_seconds() // 3600)
    days = delta.days
    years = days // 365


    if days < 1:
        return f"{hours} hour{'s' if hours != 1 else ''}"


    if years > 0:
        return f"{years} year{'s' if years != 1 else ''}"

    months = days // 30
    if months > 0:
        return f"{months} month{'s' if months > 1 else ''}"

    if days > 0:
        return f"{days} day{'s' if days != 1 else ''}"

    return f"{hours} hour{'s' if hours != 1 else ''}"


@register.filter
def is_in_favorites(animal_id, favorites_ids):
    if not favorites_ids:
        return False
    return animal_id in favorites_ids


@register.filter
def get_adoption_status(animal_id, adoption_requests):
    if not adoption_requests:
        return None
    return adoption_requests.get(animal_id)
