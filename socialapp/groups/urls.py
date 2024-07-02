from django.urls import path

from . import views

app_name = "groups"

urlpatterns = [
    path('', views.GroupListView.as_view(), name="group_list"),
    path('group/<slug:group_slug>/', views.GroupDetailView.as_view(), name="group_detail"),
    path('group/<slug:group_slug>/posts/', views.GroupPostsListView.as_view(), name="group_posts"),
    path('group/<slug:group_slug>/post/<slug:post_slug>/', views.GroupPostDetailView.as_view(), name="post_detail"),

]
