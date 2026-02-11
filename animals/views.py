from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Animal, Species, Breed

class AnimalListView(ListView):
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 12
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_available_for_adoption=True)
        
        search_query = self.request.GET.get('search', '')
        species_id = self.request.GET.get('species')
        breed_id = self.request.GET.get('breed')
        gender = self.request.GET.get('gender')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(breed__name__icontains=search_query)
            )
        
        if species_id:
            queryset = queryset.filter(species_id=species_id)
            
        if breed_id:
            queryset = queryset.filter(breed_id=breed_id)

        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset.select_related('species', 'breed').prefetch_related('photos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['species_list'] = Species.objects.all()
        context['breeds_list'] = Breed.objects.all() 
        context['gender_choices'] = Animal.GENDER_CHOICES
        return context

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['animals/includes/animal_card_list.html']
        return super().get_template_names()

class AnimalDetailView(DetailView):
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .templatetags.animal_filters import age
        animal = self.object
        age_str = age(animal.birth_date)
        
        # Construct QR code text
        qr_text = f"Name: {animal.name}\n"
        qr_text += f"Species: {animal.species.name if animal.species else 'Unknown'}\n"
        qr_text += f"Breed: {animal.breed.name if animal.breed else 'Unknown'}\n"
        qr_text += f"Age: {age_str}\n"
        qr_text += f"Health: {animal.health_status}\n"
        if animal.chip_number:
            qr_text += f"Chip: {animal.chip_number}"
            
        context['qr_text'] = qr_text
        return context
