from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.utils.text import slugify
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.conf import settings

from .utils import DataMixin
from .models import Post, TagPost, Comment
from .forms import AddPageForm, CommentCreateForm

# Create your views here.
class PostListView(DataMixin, ListView):
    template_name = "posts/index.html"
    context_object_name = "posts"
    title_page = "Главная страница"
    cat_selected = 0
    paginate_by = 10
    extra_context = {"default_image": settings.DEFAULT_USER_IMAGE}
    
    
    def get_queryset(self) -> QuerySet[Any]:
        return Post.published.all()
    

class PostDetailView(DataMixin, DetailView):
    template_name = "posts/post_detail.html"
    slug_url_kwarg = "post_slug"
    context_object_name = "post"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=context["post"].title, form=CommentCreateForm())
    
    def get_object(self, queryset=None):
        return get_object_or_404(Post.published, slug=self.kwargs[self.slug_url_kwarg])
    
class AddCommentView(View):
    def post(self, request, post_slug):
        post = get_object_or_404(Post, slug=post_slug)
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            # return redirect("post_detail", slug=post_slug)
            return HttpResponse(request.META["HTTP_REFERER"])
        return render(request, "posts/post_detail.html", {"post": post, 'form': form})


class CommentUpdateView(UpdateView):
    pass
    
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


    
class PostCreateView(DataMixin, CreateView):
    form_class = AddPageForm
    template_name = "posts/add_post.html"
    title_page = "Добавление поста"
    
    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        w = form.save()
        return super().form_valid(form)
    

    


def about(request):
    return HttpResponse("About")

def contact(request):
    return HttpResponse("Contact")