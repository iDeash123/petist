from django.views.generic import ListView, DetailView
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .models import Animal, Species, Breed

from django.template.loader import render_to_string
from .services import generate_qr_text
from .models import AdoptionRequest

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
    oob_count_html = f'<span id="favorites-count" hx-swap-oob="true" class="text-sm text-gray-500">{new_fav_count} animals</span>'

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
            oob_container_html = f'<div id="favorites-container" hx-swap-oob="true"><div class="grid grid-cols-1 md:grid-cols-2 gap-6">{animal_card_html}</div></div>'
        else:
            if new_fav_count == 0:
                empty_state_html = render_to_string(
                    "users/includes/favorites_empty.html", request=request
                )
                oob_container_html = f'<div id="favorites-container" hx-swap-oob="true">{empty_state_html}</div>'
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
                oob_container_html = f'<div id="favorites-container" hx-swap-oob="true"><div class="grid grid-cols-1 md:grid-cols-2 gap-6">{animal_card_html}</div></div>'

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

    oob_sidebar_count_html = f'<span id="sidebar-pets-count" hx-swap-oob="true" class="block text-xl font-bold text-gray-900 dark:text-white">{new_request_count}</span>'

    extra_oob_html = ""

    if is_from_profile and not is_from_my_pets:
        requests = AdoptionRequest.objects.filter(user=user).select_related('animal')
        if not requests.exists():
            empty_html = render_to_string(
                "users/includes/my_pets_empty.html", request=request
            )
            oob_mypets_list = f'<div id="adopted-pets-container" hx-swap-oob="true">{empty_html}</div>'
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
            oob_mypets_list = f'<div id="adopted-pets-container" hx-swap-oob="true"><div class="grid grid-cols-1 md:grid-cols-2 gap-6">{list_html}</div></div>'

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

        channel_layer = get_channel_layer()
        

        context = {
            "animal": adoption_request.animal,
            "has_request": True,
            "request_status": adoption_request.status,
            "from_profile": False,
            "from_my_pets": False,
        }
        

        context["variant"] = "list"
        html_list = render_to_string("animals/includes/adopt_button.html", context, request=request)
        
        context["variant"] = "detail"
        html_detail = render_to_string("animals/includes/adopt_button.html", context, request=request)
        
        context["variant"] = "primary"
        html_primary = render_to_string("animals/includes/adopt_button.html", context, request=request)


        group_name = f"user_requests_{adoption_request.user.id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "adoption_status_update",
                "html": html_list + html_detail + html_primary,
            }
        )

    return render(
        request,
        "animals/manager/includes/request_row.html",
        {"req": adoption_request},
    )
