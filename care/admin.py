from django.contrib import admin
from .models import Task, Event, ObservationLog

admin.site.register(Task)
admin.site.register(Event)
admin.site.register(ObservationLog)
