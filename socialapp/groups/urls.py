from django.urls import path

from . import views

app_name = "groups"

urlpatterns = [
    path('', views.GroupListView.as_view(), name="group_list"),
    path('group/<slug:group_slug>/', views.GroupDetailView.as_view(), name="group_detail"),
    path('group/<slug:group_slug>/posts/', views.GroupPostsListView.as_view(), name="group_posts"),
    path('group/<slug:group_slug>/post/<slug:post_slug>/', views.GroupPostDetailView.as_view(), name="post_detail"),
    path('group/<slug:group_slug>/post/<slug:post_slug>/edit/', views.GroupPostUpdateView.as_view(), name="update_post"),
    path("search_group/", views.search_post, name="search_group"),
    
    
    
    path('create_group/', views.GroupCreateView.as_view(), name="create_group"),
    path('create_post/', views.add_post, name="add_post"),
    path('group/<slug:group_slug>/create_post/', views.GroupPostCreateView.as_view(), name="add_post_in_group"),
    path('group/<slug:group_slug>/post/<slug:post_slug>/delete/', views.delete_post, name="delete_post"),
    
    
    path("group/<slug:group_slug>/post/<slug:post_slug>/comment/", views.CommentManagerView.as_view(), name="add_comment"),
    path("group/<slug:group_slug>/post/<slug:post_slug>/comment/<int:comment_id>/delete", views.CommentManagerView.as_view(), name="delete_comment"),
    path('group/<slug:group_slug>/post/<slug:post_slug>/comment/<int:comment_id>/edit/', views.CommentUpdateView.as_view(), name="comment_update"),
    path("group/<slug:group_slug>/post/<slug:post_slug>/like/", views.like_post, name="like_post"),
    
    path('group/<slug:group_slug>/follow/', views.follow_to_group, name="follow"),
]
