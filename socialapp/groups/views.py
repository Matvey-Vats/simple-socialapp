from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Group, GroupMembership, GroupPost, GroupComment
from django.views.generic import ListView, DetailView, UpdateView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, HttpResponseRedirect
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
        return GroupPost.objects.filter(group=self.group)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["group"] = Group.objects.get(slug=self.kwargs["group_slug"])
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
    pass


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
        return self.object.get_absolute_url()
    

@login_required
def add_post(request):
    if request.method == "POST":
        form = GroupPostWithGroupForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect("groups:group_posts", post.group.slug)
    else:
        form = GroupPostWithGroupForm()
        form.fields['group'].queryset = Group.objects.filter(memberships__user=request.user)
    return render(request, 'groups/group_post_create.html', {"form": form,})


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
