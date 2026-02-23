from django.db import models
from animals.models import Animal

class Task(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='care_tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', 'is_completed', '-created_at']

    def __str__(self):
        return f"{self.title} for {self.animal.name}"

class Event(models.Model):
    EVENT_TYPES = [
        ('vet', 'Veterinary Appointment'),
        ('vaccine', 'Vaccination'),
        ('checkup', 'Scheduled Checkup'),
        ('other', 'Other'),
    ]
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='care_events')
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    date = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} - {self.animal.name} on {self.date.strftime('%Y-%m-%d')}"

class ObservationLog(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='observation_logs')
    date = models.DateField(auto_now_add=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    ACTIVITY_LEVELS = [
        (1, 'Low'),
        (2, 'Normal'),
        (3, 'High'),
    ]
    activity_level = models.IntegerField(choices=ACTIVITY_LEVELS, default=2)
    
    APPETITE_LEVELS = [
        (1, 'Poor'),
        (2, 'Normal'),
        (3, 'Excellent'),
    ]
    appetite_level = models.IntegerField(choices=APPETITE_LEVELS, default=2)
    
    notes = models.TextField(blank=True, help_text="Early warning system or other observations")
    
    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Observation for {self.animal.name} on {self.date}"
