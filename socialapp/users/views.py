from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from users.models import User
from django.contrib.auth.decorators import login_required
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, ListView, DetailView, View
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
    
    
class UserProfileView(LoginRequiredMixin, DataMixin, DetailView, View):
    model = User
    template_name = "registration/users_profile.html"
    context_object_name = "profile_user"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_subscribed"] = self.request.user.subscriptions.filter(id=self.object.id).exists()
        
        context["current_user"] = User.objects.get(username=self.kwargs["username"])
        return self.get_mixin_context(context, title=context["profile_user"].username)

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs["username"]) 
    
    def post(self, request, *args, **kwargs):
        user_to_subscribe = self.get_object()
        if "subcsribe" in request.POST:
            request.user.subscriptions.add(user_to_subscribe)
        elif "unsubscribe" in request.POST:
            request.user.subscriptions.remove(user_to_subscribe)
        return redirect("profile", username=user_to_subscribe.username)
    
    
class UserSubscriptionsView(LoginRequiredMixin, ListView):
    template_name = 'registration/user_subscriptions.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.subscriptions.all()

class UserSubscribersView(LoginRequiredMixin, ListView):
    template_name = 'registration/user_subscribers.html'
    context_object_name = 'subscribers'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user.subscribers.all()
    
    
@login_required
def subscribe(request, username):
    user = get_object_or_404(User, username=username)
    request.user.subscriptions.add(user)
    return redirect('users:user_profile', username=username)

@login_required
def unsubscribe(request, username):
    user = get_object_or_404(User, username=username)
    request.user.subscriptions.remove(user)
    return redirect('users:user_profile', username=username)
