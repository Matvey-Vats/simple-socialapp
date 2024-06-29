from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.utils.text import slugify
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count

from .utils import DataMixin
from .models import Post, TagPost, Comment
from .forms import AddPageForm, CommentCreateForm

# Create your views here.
class PostListView(DataMixin, ListView):
    template_name = "posts/index.html"
    context_object_name = "posts"
    title_page = "Главная страница"
    cat_selected = 0
    paginate_by = 9
    # extra_context = {"default_image": settings.DEFAULT_USER_IMAGE}
    
    
    def get_queryset(self) -> QuerySet[Any]:
        return Post.published.all().select_related("author")
    

class PostDetailView(DataMixin, DetailView):
    template_name = "posts/post_detail.html"
    slug_url_kwarg = "post_slug"
    context_object_name = "post"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        post = context['post']
        context['liked'] = False
        if self.request.user.is_authenticated:
            context['liked'] = post.likes.filter(id=self.request.user.id).exists()
        return self.get_mixin_context(context, title=context["post"].title, form=CommentCreateForm())
    
    def get_object(self, queryset=None):
        return get_object_or_404(Post.published, slug=self.kwargs[self.slug_url_kwarg])
    
class AddCommentView(LoginRequiredMixin, View):
    
    
    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and request.POST.get("_method") == "DELETE":
            request.method = "DELETE"
        return super().dispatch(request, *args, **kwargs)
    
    
    def post(self, request, post_slug, comment_id=None):
        post = get_object_or_404(Post, slug=post_slug)
        if comment_id:
            comment = get_object_or_404(Comment, id=comment_id, post=post)
            form = CommentCreateForm(request.POST, instance=comment)
        else:
            form = CommentCreateForm(request.POST)
            
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                new_comment.parent = Comment.objects.get(id=parent_id)
                
            new_comment.save()
            return redirect("post_detail", post_slug=post_slug)
        return render(request, "posts/post_detail.html", {"post": post, 'form': form})
    
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        post_slug = comment.post.slug
        if request.user == comment.user:
            comment.delete()
        return redirect('post_detail', post_slug=post_slug)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['content']
    template_name = "posts/comment_edit.html"
    pk_url_kwarg = "comment_id"
    
    def get_success_url(self) -> str:
        post_slug = self.object.post.slug
        return reverse_lazy("post_detail", kwargs={"post_slug": post_slug})
    
class PostCategoryListView(DataMixin, ListView):
    template_name = "posts/index.html"
    context_object_name = "posts"
    allow_empty = False
    
    def get_queryset(self) -> QuerySet[Any]:
        return Post.published.filter(category__slug=self.kwargs["cat_slug"]).select_related('category')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cat = context["posts"][0].category
        return self.get_mixin_context(context, title="Категория - " + cat.name, cat_selected=cat.id)
    
class PostTagsListView(DataMixin, ListView):
    template_name = "posts/index.html"
    context_object_name = "posts"
    allow_empty = False
    
    def get_queryset(self):
        return Post.published.filter(tags__slug=self.kwargs["tag_slug"]).select_related('category')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs["tag_slug"])
        return self.get_mixin_context(context, title="Тег - " + tag.tag)


    
class PostCreateView(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPageForm
    template_name = "posts/add_post.html"
    title_page = "Добавление поста"
    
    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        w = form.save()
        return super().form_valid(form)
    
class PostUpdateView(LoginRequiredMixin, DataMixin, UpdateView):
    model = Post
    form_class = AddPageForm
    title_page = "Редактирование поста"
    template_name = "posts/add_post.html"
    
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        # if not self.request.FILES.get('photo'):
        #     post.photo = self.get_object().photo
            
        post = form.save()
        return super().form_valid(form)
        
    def get_success_url(self) -> str:
        return reverse_lazy("home")
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return get_object_or_404(Post, slug=self.kwargs["slug"])
    
    
class RecomendationListView(LoginRequiredMixin, DataMixin, ListView):
    posts_count = 30
    template_name = "posts/recomendation.html"
    title_page = "Страница рекомендаций"
    context_object_name = "most_likes_posts"
    paginate_by = 9
    
    
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        subscriptions = self.request.user.subscriptions.all()
        subscription_posts = Post.published.filter(author__in=subscriptions).order_by("-time_create").select_related("author")
        
        recommended_users = get_user_model().objects.filter(subscribers__in=subscriptions).exclude(id__in=subscriptions).distinct().select_related("author")
        recommended_posts = Post.published.filter(author__in=recommended_users).exclude(author__in=subscriptions).order_by("-time_create").select_related("author")
        combined_posts = subscription_posts | recommended_posts
        context["combined_posts"] = combined_posts.distinct()
        return self.get_mixin_context(context)
    
    
    def get_queryset(self) -> QuerySet[Any]:
        return Post.published.annotate(like_count=Count('likes')).order_by("-like_count")[:self.posts_count].select_related("author")


def search_posts(request):
    query = request.GET.get("query")
    posts = Post.published.all()
    
    if query:
        posts = Post.published.filter(title__icontains=query)
    
    context = {
        "posts": posts,
    }
    return render(request, "posts/recomendation.html", context)

def like_post(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    if request.user.is_authenticated:
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    return HttpResponseRedirect(reverse_lazy("post_detail", args=[post_slug]))


def about(request):
    return HttpResponse("About")

def contact(request):
    return HttpResponse("Contact")