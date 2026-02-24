from django.db import models
from django.conf import settings
from django.utils.text import slugify


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache


class Species(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Species"

    def __str__(self):
        return self.name


class Breed(models.Model):
    name = models.CharField(max_length=100)
    species = models.ForeignKey(
        Species, on_delete=models.CASCADE, related_name="breeds"
    )
    characteristics = models.TextField(
        blank=True, help_text="Typical traits for this breed"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "species"]

    def __str__(self):
        return f"{self.name} ({self.species.name})"


class Animal(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    name = models.CharField(max_length=100)
    species = models.ForeignKey(
        Species, on_delete=models.SET_NULL, null=True, related_name="animals"
    )
    breed = models.ForeignKey(
        Breed, on_delete=models.SET_NULL, null=True, blank=True, related_name="animals"
    )
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    chip_number = models.CharField(max_length=50, blank=True, null=True, unique=True)

    is_available_for_adoption = models.BooleanField(default=True)
    health_status = models.CharField(
        max_length=100, blank=True, help_text="Good, Needs Care, etc."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Animal.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class AnimalPhoto(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="animals/")
    is_main = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-is_main", "id"]
        verbose_name = "Animal Photo"
        verbose_name_plural = "Animal Photos"

    def __str__(self):
        return f"Photo of {self.animal.name}"


class AdoptionRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    animal = models.ForeignKey(
        Animal, on_delete=models.CASCADE, related_name="adoption_requests"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="adoption_requests",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["animal", "user"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.animal} ({self.status})"

    def save(self, *args, **kwargs):
        print(f"DEBUG: Saving AdoptionRequest {self.id} for {self.animal.name}. Status: {self.status}")
        if self.status == "approved":
            print(f"DEBUG: Marking {self.animal.name} as unavailable.")
            self.animal.is_available_for_adoption = False
            self.animal.save()
            self.user.adopted_pets.add(self.animal)
        
        
        super().save(*args, **kwargs)


@receiver([post_save, post_delete], sender=Species)
def clear_species_cache(sender, instance, **kwargs):
    cache.delete("species_list")

@receiver([post_save, post_delete], sender=Breed)
def clear_breed_cache(sender, instance, **kwargs):
    cache.delete("breeds_list")

@receiver([post_save, post_delete], sender=Animal)
def clear_animal_cache(sender, instance, **kwargs):
    cache.clear()
