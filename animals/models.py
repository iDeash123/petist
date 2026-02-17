from django.db import models
from django.utils.text import slugify


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
