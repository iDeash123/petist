from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileForm, UserUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if not hasattr(user, "profile"):
                from .models import Profile

                Profile.objects.create(user=user)

            login(request, user)

            pending_action = request.session.pop("pending_action", None)
            if pending_action:
                from animals.models import Animal

                slug = pending_action.get("slug")
                action_type = pending_action.get("type")
                try:
                    animal = Animal.objects.get(slug=slug)
                    if action_type == "adopt":
                        user.adopted_pets.add(animal)
                    elif action_type == "favorite":
                        user.favorites.add(animal)
                except Animal.DoesNotExist:
                    pass

                from django.urls import reverse

                next_url = reverse("animals:animal_detail", kwargs={"slug": slug})
            else:
                next_url = request.GET.get("next", "home")

            if request.headers.get("HX-Request"):
                response = HttpResponse()
                if next_url == "home":
                    response["HX-Redirect"] = "/"
                else:
                    response["HX-Redirect"] = next_url
                return response

            return redirect(next_url)
    else:
        form = CustomUserCreationForm()

    if request.headers.get("HX-Request"):
        return render(request, "users/partials/register_form.html", {"form": form})

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            pending_action = request.session.pop("pending_action", None)
            if pending_action:
                from animals.models import Animal

                slug = pending_action.get("slug")
                action_type = pending_action.get("type")
                try:
                    animal = Animal.objects.get(slug=slug)
                    if action_type == "adopt":
                        user.adopted_pets.add(animal)
                    elif action_type == "favorite":
                        user.favorites.add(animal)
                except Animal.DoesNotExist:
                    pass

                from django.urls import reverse

                next_url = reverse("animals:animal_detail", kwargs={"slug": slug})
            else:
                next_url = request.GET.get("next", "/")

            if request.headers.get("HX-Request"):
                response = HttpResponse()

                from django.shortcuts import resolve_url

                try:
                    redirect_url = resolve_url(next_url)
                except:
                    redirect_url = "/"

                response["HX-Redirect"] = redirect_url
                return response

            return redirect(next_url)
    else:
        form = AuthenticationForm()

    if request.headers.get("HX-Request"):
        return render(request, "users/partials/login_form.html", {"form": form})

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
@login_required
def profile_view(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("users:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "favorited_animals_ids": set(
            request.user.favorites.values_list("id", flat=True)
        ),
        "adopted_animals_ids": set(
            request.user.adopted_pets.values_list("id", flat=True)
        ),
    }

    return render(request, "users/profile.html", context)
