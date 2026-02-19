from django.contrib import admin
from .models import Species, Breed, Animal, AnimalPhoto, AdoptionRequest


class AnimalPhotoInline(admin.TabularInline):
    model = AnimalPhoto
    extra = 1


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "species",
        "breed",
        "birth_date",
        "gender",
        "is_available_for_adoption",
    )
    list_filter = ("species", "gender", "is_available_for_adoption")
    search_fields = ("name", "chip_number", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [AnimalPhotoInline]


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ("animal", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("animal__name", "user__username", "user__email")
    actions = ["approve_requests", "reject_requests"]

    def approve_requests(self, request, queryset):
        for adoption_request in queryset:
            if adoption_request.status != "approved":
                adoption_request.status = "approved"
                adoption_request.save()
                
                animal = adoption_request.animal
                animal.is_available_for_adoption = False
                animal.save()
                
                adoption_request.user.adopted_pets.add(animal)
                
        self.message_user(request, "Selected requests have been approved.")
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        queryset.update(status="rejected")
        self.message_user(request, "Selected requests have been rejected.")
    reject_requests.short_description = "Reject selected requests"

    actions = ["approve_requests", "reject_requests", "sync_availability"]

    def sync_availability(self, request, queryset):
        count = 0
        for req in queryset:
            if req.status == "approved" and req.animal.is_available_for_adoption:
                req.animal.is_available_for_adoption = False
                req.animal.save()
                count += 1
        self.message_user(request, f"Synced {count} animals to unavailable.")
    sync_availability.short_description = "Sync animal availability (Fix)"


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ("name", "species")
    list_filter = ("species",)
    search_fields = ("name",)
