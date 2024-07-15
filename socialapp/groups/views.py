from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Group, GroupMembership, GroupPost, GroupComment
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, View
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse_lazy

from posts.utils import DataMixin
from groups.forms import CommentCreateForm, GroupCreateForm, GroupPostWithGroupForm, GroupPostForm


class GroupListView(LoginRequiredMixin, DataMixin, ListView):
    model = Group
    template_name = "groups/group_list.html"
    context_object_name = "groups"
    title_page = "Группы"
    paginate_by = 12
    
    def get_queryset(self) -> QuerySet[Any]:
        return Group.objects.filter(privacy=Group.Status.OPEN).select_related("owner")
    
    
class GroupDetailView(LoginRequiredMixin, DataMixin, DetailView):
    model = Group
    template_name = "groups/group_detail.html"
    context_object_name = "group"
    slug_url_kwarg = "group_slug"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context['members'] = GroupMembership.objects.filter(group=group)
        context['has_posts'] = GroupPost.objects.filter(group=group).exists()
        context["user_is_member"] = group.memberships.filter(user=self.request.user).exists()
        return self.get_mixin_context(context, title="Группа - " + group.name)
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return Group.objects.get(slug=self.kwargs[self.slug_url_kwarg], privacy=Group.Status.OPEN)
    

class GroupPostsListView(LoginRequiredMixin, DataMixin, ListView):
    model = GroupPost
    template_name = "groups/group_posts_list.html"
    context_object_name = "posts"
    paginate_by = 10
    
    def get_queryset(self) -> QuerySet[Any]:
        self.group = get_object_or_404(Group, slug=self.kwargs["group_slug"])
        return GroupPost.objects.filter(group=self.group).select_related("author")
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["group"] = Group.objects.get(slug=self.kwargs["group_slug"])
        context["user_is_member"] = context["group"].memberships.filter(user=self.request.user).exists()
        return self.get_mixin_context(context, title="Посты группы " + context['group'].name)
    
    
class GroupPostDetailView(LoginRequiredMixin, DataMixin, DetailView):
    model = GroupPost
    template_name = "groups/post_detail.html"
    context_object_name = "post"
    slug_url_kwarg = "post_slug"
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        self.group = get_object_or_404(Group, slug=self.kwargs["group_slug"])
        return get_object_or_404(GroupPost, group=self.group, slug=self.kwargs[self.slug_url_kwarg])
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(Group, slug=self.kwargs["group_slug"])
        post = context['post']
        context['liked'] = False
        if self.request.user.is_authenticated:
            context['liked'] = post.likes.filter(id=self.request.user.id).exists()
        return self.get_mixin_context(context, title='Пост ' + context["post"].title, form=CommentCreateForm())
    
class GroupPostUpdateView(LoginRequiredMixin, DataMixin, UpdateView):
    model = GroupPost
    form_class = GroupPostForm
    template_name = "groups/group_post_create.html"
    slug_url_kwarg = "post_slug"
    
    def get_success_url(self) -> str:
        group_slug = self.kwargs['group_slug']
        return reverse_lazy("groups:group_posts", kwargs={'group_slug': group_slug})

# class GroupPostDeleteView(LoginRequiredMixin, DeleteView):
#     model = GroupPost
#     template_name = "groups/post_detail.html"
#     success_url = reverse_lazy("home")
#     slug_url_kwarg = "post_slug"
    
#     def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
#         return get_object_or_404(GroupPost, slug=self.slug_url_kwarg, group__slug=self.kwargs['group_slug'])
    
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['group_slug'] = self.kwargs.get('group_slug')
#         return context

    
@login_required
def delete_post(request, group_slug, post_slug):
    group = get_object_or_404(Group, slug=group_slug, privacy=Group.Status.OPEN)
    post = get_object_or_404(GroupPost, slug=post_slug, group=group)
    post.delete()
    return redirect("groups:group_posts", group_slug)    

class GroupCreateView(LoginRequiredMixin, DataMixin, CreateView):
    form_class = GroupCreateForm
    template_name = "groups/group_create.html"
    title_page = "Создание группы"
    
    
    def form_valid(self, form):
        group = form.save(commit=False)
        group.owner = self.request.user
        group = form.save()
        return super().form_valid(form)
    
    
class GroupPostCreateView(LoginRequiredMixin, DataMixin, CreateView):
    form_class = GroupPostForm
    template_name = "groups/group_post_create.html"
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.group = get_object_or_404(Group, slug=self.kwargs["group_slug"])
        return super().form_valid(form)
    
    def get_success_url(self) -> str:
        group_slug = self.kwargs["group_slug"]
        post_slug = self.object.slug
        return reverse_lazy("groups:post_detail", kwargs={'group_slug': group_slug, 'post_slug': post_slug})
    

@login_required
def add_post(request):
    if request.method == "POST":
        form = GroupPostWithGroupForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.owner = request.user  # Назначаем владельцем поста текущего пользователя
            post.save()
            form.save_m2m()
            return redirect("groups:group_posts", group_slug=post.group.slug)
        else:
            print(form.errors)  # Отладочное сообщение
    else:
        form = GroupPostWithGroupForm(user=request.user)
    return render(request, 'groups/group_post_create.html', {"form": form})

class CommentManagerView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and request.POST.get("_method") == "DELETE":
            request.method = "DELETE"
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, group_slug, post_slug, comment_id=None):
        group = get_object_or_404(Group, slug=group_slug)
        post = get_object_or_404(GroupPost, slug=post_slug, group=group)
        if comment_id:
            comment = get_object_or_404(GroupComment, id=comment_id, post=post)
            form = CommentCreateForm(request.POST, instance=comment)
        else:
            form = CommentCreateForm(request.POST)
        
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                new_comment.parent = GroupComment.objects.get(id=parent_id)
            
            new_comment.save()
            return redirect("groups:post_detail", group_slug=group_slug, post_slug=post_slug)
        
        return render(request, "groups/post_detail.html", {"group": group, "post": post, "form": form})

    def delete(self, request, group_slug, post_slug, comment_id):
        comment = get_object_or_404(GroupComment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
        return redirect('groups:post_detail', group_slug=group_slug, post_slug=post_slug)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = GroupComment
    fields = ['content']
    template_name = "groups/comment_edit.html"
    pk_url_kwarg = "comment_id"
    
    def get_success_url(self) -> str:
        post_slug = self.object.post.slug
        group_slug = self.object.post.group.slug
        return reverse_lazy("groups:post_detail", kwargs={"post_slug": post_slug,
                                                   "group_slug": group_slug})

class UsersListView(LoginRequiredMixin, DataMixin, ListView):
    model = get_user_model()
    template_name = "groups/user_list.html"
    context_object_name = "users"
    title_page = "Выберете пользователя"
    
    def get_queryset(self) -> QuerySet[Any]:
        current_user = self.request.user
        subscriptions = current_user.subscriptions.all()
        others = get_user_model().objects.exclude(id__in=subscriptions).exclude(id=current_user.id)
        
        queryset = list(subscriptions) + list(others)
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        users = get_user_model().objects.all()
        context['group'] = get_object_or_404(Group, slug=self.kwargs["group_slug"])
        context['subscriptions'] = current_user.subscriptions.all()
        context['user_in_group'] = context["group"].memberships.filter(user=current_user).exists()
        context['user_membership_info'] = [
        (user, GroupMembership.objects.filter(group=context['group'], user=user).exists())
        for user in users
    ]
        return context
        
@login_required
def like_post(request, group_slug, post_slug):
    group = get_object_or_404(Group, slug=group_slug)
    post = get_object_or_404(GroupPost, group=group, slug=post_slug)
    if request.user.is_authenticated:
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    return HttpResponseRedirect(reverse_lazy("groups:post_detail", kwargs={"group_slug": group_slug, "post_slug": post_slug,}))


@login_required
def follow_to_group(request, group_slug):
    group = get_object_or_404(Group, slug=group_slug, privacy=Group.Status.OPEN)
    user = request.user
    new_member = GroupMembership.objects.create(group=group, user=user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

@login_required
def add_user_to_group(request, group_slug, username):
    group = get_object_or_404(Group, slug=group_slug)
    user = get_object_or_404(get_user_model(), username=username)
    new_member = GroupMembership.objects.create(group=group, user=user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
    
def search_post(request):
    query = request.GET.get('query')
    
    if query:
        searched_group = Group.objects.filter(
            Q(privacy=Group.Status.OPEN) | Q(privacy=Group.Status.CLOSED),
            name__icontains=query
        )
    
    return render(request, "groups/group_list.html", {"groups": searched_group})