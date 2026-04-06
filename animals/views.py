from django.views.generic import ListView, DetailView
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .models import Animal, Species, Breed, AnimalPhoto

from django.template.loader import render_to_string
from .services import generate_qr_text
from .models import AdoptionRequest

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync


@login_required
@require_POST
def toggle_favorite(request, slug):
    animal = get_object_or_404(Animal, slug=slug)
    user = request.user

    if animal in user.favorites.all():
        user.favorites.remove(animal)
        is_favorited = False
    else:
        user.favorites.add(animal)
        is_favorited = True

    is_from_profile = request.GET.get("from_profile") == "1"
    is_from_my_pets = request.GET.get("from_my_pets") == "1"

    new_fav_count = user.favorites.count()
    oob_count_html = render_to_string(
        "users/includes/favorites_count_oob.html",
        {"new_fav_count": new_fav_count},
        request=request
    )

    extra_oob_html = ""

    if is_from_profile and not is_from_my_pets:
        context = {
            "animal": animal,
            "is_favorited": is_favorited,
            "from_profile": True,
            "from_my_pets": True,
        }

        btn_html = render_to_string(
            "animals/includes/favorite_button.html", context, request=request
        )
        btn_html = btn_html.replace("<button", '<button hx-swap-oob="true"', 1)
        extra_oob_html += btn_html

    if is_from_profile and not is_from_my_pets and not is_favorited:
        if new_fav_count == 0:
            empty_state_html = render_to_string(
                "users/includes/favorites_empty.html", request=request
            )
            response = HttpResponse(empty_state_html + oob_count_html + extra_oob_html)
            response["HX-Retarget"] = "#favorites-container"
            response["HX-Reswap"] = "innerHTML"
            return response

        response = HttpResponse(oob_count_html + extra_oob_html)
        response["HX-Retarget"] = f"#animal-card-{animal.id}-list"
        response["HX-Reswap"] = "outerHTML"
        return response

    if is_from_my_pets:
        if is_favorited:
            remaining_favorites = user.favorites.all()
            context = {
                "animals": remaining_favorites,
                "favorited_animals_ids": set(
                    user.favorites.values_list("id", flat=True)
                ),
                "adoption_requests": {
                    req.animal_id: req.status
                    for req in AdoptionRequest.objects.filter(user=user)
                },
                "from_profile": True,
                "show_adopt_button": True,
            }
            animal_card_html = render_to_string(
                "animals/includes/animal_card_list.html", context, request=request
            )
            oob_container_html = render_to_string(
                "users/includes/favorites_container_oob.html",
                {"inner_html": animal_card_html, "unwrap": False},
                request=request
            )
        else:
            if new_fav_count == 0:
                empty_state_html = render_to_string(
                    "users/includes/favorites_empty.html", request=request
                )
                oob_container_html = render_to_string(
                    "users/includes/favorites_container_oob.html",
                    {"inner_html": empty_state_html, "unwrap": True},
                    request=request
                )
            else:
                remaining_favorites = user.favorites.all()
                context = {
                    "animals": remaining_favorites,
                    "favorited_animals_ids": set(
                        user.favorites.values_list("id", flat=True)
                    ),
                    "adoption_requests": {
                        req.animal_id: req.status
                        for req in AdoptionRequest.objects.filter(user=user)
                    },
                    "from_profile": True,
                    "show_adopt_button": True,
                }
                animal_card_html = render_to_string(
                    "animals/includes/animal_card_list.html", context, request=request
                )
                oob_container_html = render_to_string(
                    "users/includes/favorites_container_oob.html",
                    {"inner_html": animal_card_html, "unwrap": False},
                    request=request
                )

        button_context = {
            "animal": animal,
            "is_favorited": is_favorited,
            "from_profile": True,
            "from_my_pets": True,
        }
        button_html = render_to_string(
            "animals/includes/favorite_button.html", button_context, request=request
        )
        return HttpResponse(button_html + oob_count_html + oob_container_html)

    context = {
        "animal": animal,
        "is_favorited": is_favorited,
        "from_profile": is_from_profile,
    }

    context["variant"] = request.POST.get("variant", "list")
    template_name = "animals/includes/favorite_button.html"

    html = render_to_string(template_name, context, request=request)

    return HttpResponse(html + oob_count_html + extra_oob_html)


@login_required
@require_POST
def toggle_adoption(request, slug):
    animal = get_object_or_404(Animal, slug=slug)
    user = request.user

    existing_request = AdoptionRequest.objects.filter(animal=animal, user=user).first()
    
    if existing_request:
        if existing_request.status == 'pending':
            existing_request.delete()
            has_request = False
            request_status = None
        else:
            has_request = True
            request_status = existing_request.status
    else:
        AdoptionRequest.objects.create(animal=animal, user=user)
        has_request = True
        request_status = 'pending'

    is_from_profile = request.GET.get("from_profile") == "1"
    is_from_my_pets = request.GET.get("from_my_pets") == "1"

    new_request_count = AdoptionRequest.objects.filter(user=user).count()

    oob_sidebar_count_html = render_to_string(
        "users/includes/sidebar_pets_count_oob.html",
        {"new_request_count": new_request_count},
        request=request
    )

    extra_oob_html = ""

    if is_from_profile and not is_from_my_pets:
        requests = AdoptionRequest.objects.filter(user=user).select_related('animal')
        if not requests.exists():
            empty_html = render_to_string(
                "users/includes/my_pets_empty.html", request=request
            )
            oob_mypets_list = render_to_string(
                "users/includes/adopted_pets_container_oob.html",
                {"inner_html": empty_html, "unwrap": True},
                request=request
            )
        else:
            context = {
                "animals": [req.animal for req in requests],
                "favorited_animals_ids": set(
                    user.favorites.values_list("id", flat=True)
                ),
                "adoption_requests": {
                    req.animal_id: req.status for req in requests
                },
                "from_profile": True,
                "from_my_pets": True,
                "show_adopt_button": True,
            }
            list_html = render_to_string(
                "animals/includes/animal_card_list.html", context, request=request
            )
            oob_mypets_list = render_to_string(
                "users/includes/adopted_pets_container_oob.html",
                {"inner_html": list_html, "unwrap": False},
                request=request
            )

        extra_oob_html += oob_mypets_list

    if is_from_my_pets:
        if not has_request: 
             if new_request_count == 0:
                empty_state_html = render_to_string(
                    "users/includes/my_pets_empty.html", request=request
                )
                response = HttpResponse(
                    empty_state_html + oob_sidebar_count_html + extra_oob_html
                )
                response["HX-Retarget"] = "#adopted-pets-container"
                response["HX-Reswap"] = "innerHTML"
                return response
             
             response = HttpResponse(oob_sidebar_count_html + extra_oob_html)
             response["HX-Retarget"] = f"#animal-card-{animal.id}-mypets"
             response["HX-Reswap"] = "delete"
             return response

    context = {
        "animal": animal,
        "has_request": has_request,
        "request_status": request_status,
        "from_profile": is_from_profile,
        "from_my_pets": is_from_my_pets,
    }

    context["variant"] = request.POST.get("variant", "list")
    template_name = "animals/includes/adopt_button.html"

    html = render_to_string(template_name, context, request=request)
    return HttpResponse(html + oob_sidebar_count_html + extra_oob_html)


class AnimalListView(ListView):
    model = Animal
    template_name = "animals/animal_list.html"
    context_object_name = "animals"
    paginate_by = 12
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_available_for_adoption=True)

        search_query = self.request.GET.get("q", "")
        species_id = self.request.GET.get("species")
        breed_id = self.request.GET.get("breed")
        gender = self.request.GET.get("gender")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(breed__name__icontains=search_query)
            )

        if species_id:
            queryset = queryset.filter(species_id=species_id)

        if breed_id:
            queryset = queryset.filter(breed_id=breed_id)

        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset.select_related("species", "breed").prefetch_related("photos")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        species_list = cache.get("species_list")
        if species_list is None:
            species_list = list(Species.objects.all())
            cache.set("species_list", species_list, 60 * 60 * 24)
        context["species_list"] = species_list

        breeds_list = cache.get("breeds_list")
        if breeds_list is None:
            breeds_list = list(Breed.objects.all())
            cache.set("breeds_list", breeds_list, 60 * 60 * 24)
        context["breeds_list"] = breeds_list

        context["gender_choices"] = Animal.GENDER_CHOICES
        if self.request.user.is_authenticated:
            context["favorited_animals_ids"] = set(
                self.request.user.favorites.values_list("id", flat=True)
            )
            context["adoption_requests"] = {
                req.animal_id: req.status 
                for req in AdoptionRequest.objects.filter(user=self.request.user)
            }
        else:
            context["favorited_animals_ids"] = set()
            context["adoption_requests"] = {}

        context["show_adopt_button"] = True
        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Target") == "animal-grid":
            return ["animals/includes/animal_card_list.html"]
        return super().get_template_names()


def start_adoption(request, slug):
    request.session["pending_action"] = {"type": "adopt", "slug": slug}
    response = HttpResponse(status=204)
    response["HX-Trigger"] = '{"open-auth-modal": {"type": "login"}}'
    return response


def start_favorite(request, slug):
    request.session["pending_action"] = {"type": "favorite", "slug": slug}
    response = HttpResponse(status=204)
    response["HX-Trigger"] = '{"open-auth-modal": {"type": "login"}}'
    return response


class AnimalDetailView(DetailView):
    model = Animal
    template_name = "animals/animal_detail.html"
    context_object_name = "animal"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        animal = self.object

        context["qr_text"] = generate_qr_text(animal)
        if self.request.user.is_authenticated:
            context["is_favorited"] = animal in self.request.user.favorites.all()
            adoption_req = AdoptionRequest.objects.filter(animal=animal, user=self.request.user).first()
            context["has_request"] = adoption_req is not None
            context["request_status"] = adoption_req.status if adoption_req else None
        else:
            context["is_favorited"] = False
            context["has_request"] = False
            context["request_status"] = None
        return context


class ManagerAdoptionRequestListView(UserPassesTestMixin, ListView):
    model = AdoptionRequest
    template_name = "animals/manager/request_list.html"
    context_object_name = "requests"
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return super().get_queryset().select_related("user", "animal").order_by("-created_at")


@staff_member_required
@require_POST
def manager_update_request_status(request, pk):
    adoption_request = get_object_or_404(AdoptionRequest, pk=pk)
    new_status = request.POST.get("status")

    if new_status in dict(AdoptionRequest.STATUS_CHOICES):
        adoption_request.status = new_status
        adoption_request.save()

    return render(
        request,
        "animals/manager/includes/request_row.html",
        {"req": adoption_request},
    )


@staff_member_required
def animal_create(request):
    from .forms import AnimalForm

    if request.method == "POST":
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            animal = form.save()
            photo_file = form.cleaned_data.get("photo")
            if photo_file:
                AnimalPhoto.objects.create(animal=animal, image=photo_file, is_main=True)

            animal = Animal.objects.select_related("species", "breed").prefetch_related("photos").get(pk=animal.pk)

            context = {
                "animals": [animal],
                "favorited_animals_ids": set(),
                "adoption_requests": {},
                "show_adopt_button": True,
            }
            card_html = render_to_string(
                "animals/includes/animal_card_list.html", context, request=request
            )
            oob_html = render_to_string(
                "animals/includes/animal_grid_oob.html",
                {"card_html": card_html},
                request=request
            )
            success_html = render_to_string(
                "animals/includes/animal_create_success.html", request=request
            )
            response = HttpResponse(success_html + oob_html)
            response["HX-Trigger"] = "animalCreated"
            return response
        else:
            return render(request, "animals/includes/animal_form.html", {"form": form})

    form = AnimalForm()
    return render(request, "animals/includes/animal_form.html", {"form": form})


def load_breeds(request):
    species_id = request.GET.get("species")
    breeds = Breed.objects.filter(species_id=species_id) if species_id else Breed.objects.none()
    return render(request, "animals/includes/breed_options.html", {"breeds": breeds})
