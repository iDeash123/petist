from django import forms
from .models import Event, ObservationLog

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'date', 'notes']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl focus:ring-brand-500 focus:border-brand-500 px-4 py-3 shadow-sm [color-scheme:light] dark:[color-scheme:dark]'}),
            'title': forms.TextInput(attrs={'class': 'w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl focus:ring-brand-500 focus:border-brand-500 px-4 py-3 shadow-sm', 'placeholder': 'e.g. Annual Checkup'}),
            'event_type': forms.Select(attrs={'class': 'w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl focus:ring-brand-500 focus:border-brand-500 px-4 py-3 shadow-sm'}),
            'notes': forms.Textarea(attrs={'class': 'w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl focus:ring-brand-500 focus:border-brand-500 px-4 py-3 shadow-sm', 'rows': 3, 'placeholder': 'Any additional notes...'})
        }

class ObservationLogForm(forms.ModelForm):
    class Meta:
        model = ObservationLog
        fields = ['weight_kg', 'activity_level', 'appetite_level', 'notes']
        widgets = {
            'weight_kg': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl focus:ring-brand-500 focus:border-brand-500 px-4 py-3 shadow-sm', 'step': '0.01'}),
            'activity_level': forms.Select(attrs={'class': 'w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl focus:ring-brand-500 focus:border-brand-500 px-4 py-3 shadow-sm'}),
            'appetite_level': forms.Select(attrs={'class': 'w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl focus:ring-brand-500 focus:border-brand-500 px-4 py-3 shadow-sm'}),
            'notes': forms.Textarea(attrs={'class': 'w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl focus:ring-brand-500 focus:border-brand-500 px-4 py-3 shadow-sm', 'rows': 3, 'placeholder': 'Any notable observations...'})
        }
