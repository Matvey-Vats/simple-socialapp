from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Group, GroupMembership, GroupPost
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from posts.utils import DataMixin


class GroupListView(LoginRequiredMixin, DataMixin, ListView):
    model = Group
    template_name = "groups/group_list.html"
    context_object_name = "groups"
    title_page = "Группы"
    
    
    def get_queryset(self) -> QuerySet[Any]:
        return Group.objects.filter(privacy=Group.Status.OPEN)
    
    
class GroupDetailView(LoginRequiredMixin, DataMixin, DetailView):
    model = Group
    template_name = "groups/group_detail.html"
    context_object_name = "group"
    slug_url_kwarg = "group_slug"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context['members'] = GroupMembership.objects.filter(group=group)
        return self.get_mixin_context(context, title="Группа - " + group.name)
    
    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return Group.objects.get(slug=self.kwargs[self.slug_url_kwarg], privacy=Group.Status.OPEN)
    
