from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def index(request):
    """Домашняя страница приложения learning_log"""
    return render(request, 'learning_logs/index.html')


@login_required
def topics(request):
    """Выводит список тем"""
    if request.user.username == 'admin':
        topics = Topic.objects.all()
    else:
        topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """Выводит одну тему и все ее записи"""
    topic = get_object_or_404(Topic, pk=topic_id)
    check_topic_owner(request, topic)

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Определяет новую тему"""
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма
        form = TopicForm()
    else:
        # Отправлены данные POST; обработать данные
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    # Вывести пустую или недействительную форму
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


def delete_topic(request, topic_id):
    """Удаляет существующую тему"""
    topic = get_object_or_404(Topic, pk=topic_id)
    check_topic_owner(request, topic)

    topic.delete()
    return redirect('learning_logs:topics')


@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме"""
    topic = get_object_or_404(Topic, pk=topic_id)
    check_topic_owner(request, topic)
    if request.method != 'POST':
        # Данные не отправлялись, создается пустая форма
        form = EntryForm()
    else:
        # Отправлены данные POST; обработать данные
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Вывести пустую или недействительную форму
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись"""
    entry = get_object_or_404(Entry, pk=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)

    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST; обработать данные
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)


@login_required
def delete_entry(request, entry_id):
    """Удаляет существующую запись"""
    entry = get_object_or_404(Entry, pk=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)

    entry.delete()
    return redirect('learning_logs:topic', topic_id=topic.id)


def check_topic_owner(request, topic):
    """Проверяет связь между пользователем и темой"""
    if topic.owner != request.user and request.user.username != 'admin':
        raise Http404