from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from animals.models import Animal
from .models import Task

@login_required
def dashboard(request):
    adopted_animals = request.user.adopted_pets.all()
    if adopted_animals.count() == 1:
        return redirect('care:animal_dashboard', animal_id=adopted_animals.first().id)
    return render(request, 'care/dashboard_index.html', {'animals': adopted_animals})

@login_required
def animal_care_dashboard(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    
    if animal not in request.user.adopted_pets.all() and not request.user.is_superuser:
        return redirect('home')
        
    tasks = animal.care_tasks.all()
    events = animal.care_events.all()
    observations = animal.observation_logs.all()
    
    context = {
        'animal': animal,
        'tasks': tasks,
        'events': events,
        'observations': observations,
    }
    return render(request, 'care/animal_dashboard.html', context)

@login_required
def toggle_task(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id)
        if task.animal not in request.user.adopted_pets.all() and not request.user.is_superuser:
            return redirect('home')
            
        task.is_completed = not task.is_completed
        task.save()
        
        return render(request, 'care/partials/task_item.html', {'task': task})
    return redirect('home')

@login_required
@require_POST
def add_task(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    if animal not in request.user.adopted_pets.all() and not request.user.is_superuser:
        return redirect('home')
        
    title = request.POST.get('title')
    due_date = request.POST.get('due_date')
    
    if title:
        task = Task.objects.create(
            animal=animal,
            title=title,
            due_date=due_date if due_date else None
        )
        return render(request, 'care/partials/task_item.html', {'task': task})
        
    return redirect('care:animal_dashboard', animal_id=animal.id)

@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.animal not in request.user.adopted_pets.all() and not request.user.is_superuser:
        return redirect('home')
        
    task.delete()
    return HttpResponse('')
