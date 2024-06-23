from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView
from django.conf import settings


from .forms import UserLoginForm, RegistrationUserForm, UserProfileForm

class LoginUser(LoginView):
    form_class = UserLoginForm
    template_name = "registration/login.html"
    extra_context = {"title": "Авторизация",}
    
    def get_success_url(self) -> str:
        return reverse_lazy("home")

class RegisterUser(CreateView):
    form_class = RegistrationUserForm
    template_name = "registration/registration.html"
    extra_context = {"title": "Регистрация",}
    success_url = reverse_lazy("users:login")
    

class ProfileUserView(UpdateView):
    model = get_user_model()
    form_class = UserProfileForm
    template_name = "registration/profile.html"
    extra_context = {
        'title': "Профиль пользователя",
        'default_image': settings.DEFAULT_USER_IMAGE,
    }

    def get_success_url(self) -> str:
        return reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user





class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")