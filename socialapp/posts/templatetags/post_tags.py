from django import template
from django.db.models import Count
from posts.models import Category, TagPost, Post

register = template.Library()


@register.inclusion_tag("posts/list_categories.html") 
def show_categories(cat_selected=0, count=15):
    cats = Category.objects.annotate(num_posts=Count("posts")).filter(num_posts__gt=0).order_by('-num_posts')[:count]
    return {'cats': cats, 'cat_selected': cat_selected, }

@register.inclusion_tag("posts/list_tags.html")
def show_populate_tags(count=15):
    # return {'tags': TagPost.objects.annotate(total=Count("tags")).filter(total__gt=0), }
    return {"tags": TagPost.objects.annotate(num_posts=Count('tags')).filter(num_posts__gt=0).order_by('-num_posts')[:count]}

def get_popular_posts(count=30):
    return {"posts": Post.published.annotate(like_count=Count("likes")).order_by("-like_count")[:count]}



@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except(ValueError, TypeError):
        return ''