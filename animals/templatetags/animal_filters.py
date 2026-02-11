from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def age(birth_date):
    if not birth_date:
        return ""
    
    # Convert date to datetime at midnight (start of day)
    import datetime
    start_of_day = datetime.datetime.combine(birth_date, datetime.time.min)
    # Make it aware if settings use TZ
    if timezone.is_aware(timezone.now()):
        start_of_day = timezone.make_aware(start_of_day)
        
    now = timezone.now()
    delta = now - start_of_day
    
    if delta.total_seconds() < 0:
        return "Not born yet"
        
    # Calculate components
    hours = int(delta.total_seconds() // 3600)
    days = delta.days
    years = days // 365
    
    # "If it was today, solve in hours"
    if days < 1:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    
    # "If it was a year ago, only show years"
    if years > 0:
        return f"{years} year{'s' if years != 1 else ''}"

    # "If it was a month ago, only show months"
    months = days // 30
    if months > 0:
        return f"{months} month{'s' if months > 1 else ''}"
        
    # "If it was days ago, only show days"
    if days > 0:
        return f"{days} day{'s' if days != 1 else ''}"

    return f"{hours} hour{'s' if hours != 1 else ''}"
