# from django.forms import BaseModelForm
# from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

# Vista para login
class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    
    #Si ya esta logueado se salta esta página
    redirect_authenticated_user = True
    
    #Si se loguea con exito
    def get_success_url(self):
        return reverse_lazy('tasks')
    
#Vista para registrarse
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

#Lista de tareas
class TaskList(LoginRequiredMixin,ListView):
   model = Task
   context_object_name = 'tasks'
   
   # Función para que cada persona solo pueda ver sus tareas
   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       context['tasks'] = context['tasks'].filter(user=self.request.user)
       context['count'] = context['tasks'].filter(complete=False).count()
       
       search_input = self.request.GET.get('search-area') or ''
       if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)
            
       context['search_input'] = search_input      
            
       return context
   
# Vista de detalle
class TaskDetail(LoginRequiredMixin, DetailView):
   model = Task
   context_object_name = 'task'
   template_name = 'base/task.html'

#Vista para Crear
class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    
    # Método para asignar automáticamente la tarea a la persona adecuada
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

#Vista para Editar  
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    
#Vista para Borrar  
class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')