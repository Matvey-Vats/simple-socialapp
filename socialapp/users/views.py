from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from users.models import User
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from posts.utils import DataMixin
from posts.models import Post, Comment


from .forms import UserLoginForm, RegistrationUserForm, UserProfileForm

class LoginUser(LoginView):
    form_class = UserLoginForm
    template_name = "registration/login.html"
    extra_context = {"title": "Авторизация",}
    success_url = reverse_lazy("home")
    
    # def get_success_url(self) -> str:
    #     return reverse_lazy("home")

class RegisterUser(CreateView):
    form_class = RegistrationUserForm
    template_name = "registration/registration.html"
    extra_context = {"title": "Регистрация",}
    success_url = reverse_lazy("users:login")
    

class ProfileUserView(LoginRequiredMixin, UpdateView):
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
    
    
class MyPostListView(DataMixin, ListView):
    model = Post
    template_name = "registration/my_posts.html"
    context_object_name = "posts"
    
    def get_queryset(self):
        return Post.published.filter(author=self.request.user)
    
class FavoriteListView(DataMixin, ListView):
    model = Post
    template_name = "registration/favorite_posts.html"
    context_object_name = "posts"
    
    def get_queryset(self):
        return Post.published.filter(likes=self.request.user)
    
class CommentsListView(DataMixin, ListView):
    model = Comment
    template_name = "registration/my_comments.html"
    context_object_name = "comments"
    
    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)
    
    