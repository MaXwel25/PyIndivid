from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from .models import Exhibition, Session
from .forms import ExhibitionForm, SessionForm

def home(request):
    exhibitions = Exhibition.objects.all()
    return render(request, 'museum/home.html', {'exhibitions': exhibitions})

def exhibition_detail(request, pk):
    exhibition = get_object_or_404(Exhibition, pk=pk)
    sessions = Session.objects.filter(exhibition=exhibition)
    return render(request, 'museum/detail.html', {
        'exhibition': exhibition,
        'sessions': sessions
    })

def add_exhibition(request):
    if request.method == 'POST':
        form = ExhibitionForm(request.POST)
        if form.is_valid():
            try:
                # Сохраняем с вызовом полной валидации
                exhibition = form.save(commit=False)
                exhibition.full_clean()  # Это вызовет clean() метод модели
                exhibition.save()
                return redirect('home')
            except ValidationError as e:
                # Добавляем ошибки модели в форму
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
    else:
        form = ExhibitionForm()
    
    return render(request, 'museum/form.html', {'form': form, 'title': 'Добавить выставку'})

def edit_exhibition(request, pk):
    exhibition = get_object_or_404(Exhibition, pk=pk)
    
    if request.method == 'POST':
        form = ExhibitionForm(request.POST, instance=exhibition)
        if form.is_valid():
            try:
                exhibition = form.save(commit=False)
                exhibition.full_clean()
                exhibition.save()
                return redirect('exhibition_detail', pk=pk)
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
    else:
        form = ExhibitionForm(instance=exhibition)
    
    return render(request, 'museum/form.html', {'form': form, 'title': 'Редактировать выставку'})
