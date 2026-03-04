from django import forms
from .models import Animal, AnimalPhoto


TAILWIND_INPUT = "w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-colors"
TAILWIND_SELECT = "w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-4 py-2.5 focus:ring-brand-500 focus:border-brand-500"
TAILWIND_TEXTAREA = "w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-colors resize-none"


class AnimalForm(forms.ModelForm):
    photo = forms.ImageField(required=False)

    class Meta:
        model = Animal
        fields = [
            "name",
            "species",
            "breed",
            "birth_date",
            "gender",
            "description",
            "chip_number",
            "health_status",
            "is_available_for_adoption",
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": TAILWIND_INPUT,
                "placeholder": "Animal name",
            }),
            "species": forms.Select(attrs={
                "class": TAILWIND_SELECT,
            }),
            "breed": forms.Select(attrs={
                "class": TAILWIND_SELECT,
            }),
            "birth_date": forms.DateInput(attrs={
                "class": TAILWIND_INPUT,
                "type": "date",
            }),
            "gender": forms.Select(attrs={
                "class": TAILWIND_SELECT,
            }),
            "description": forms.Textarea(attrs={
                "class": TAILWIND_TEXTAREA,
                "rows": 3,
                "placeholder": "Tell us about this animal...",
            }),
            "chip_number": forms.TextInput(attrs={
                "class": TAILWIND_INPUT,
                "placeholder": "Microchip number",
            }),
            "health_status": forms.TextInput(attrs={
                "class": TAILWIND_INPUT,
                "placeholder": "e.g. Healthy, Needs Care",
            }),
            "is_available_for_adoption": forms.CheckboxInput(attrs={
                "class": "w-5 h-5 text-brand-600 focus:ring-brand-500 border-gray-300 dark:border-gray-600 dark:bg-gray-700 rounded",
            }),
        }
