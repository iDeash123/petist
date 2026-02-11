from django.contrib import admin
from .models import Species, Breed, Animal, AnimalPhoto

class AnimalPhotoInline(admin.TabularInline):
    model = AnimalPhoto
    extra = 1

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'birth_date', 'gender', 'is_available_for_adoption')
    list_filter = ('species', 'gender', 'is_available_for_adoption')
    search_fields = ('name', 'chip_number', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AnimalPhotoInline]

@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'species')
    list_filter = ('species',)
    search_fields = ('name',)
