from django.urls import path

from . import views


# app_name = 'posts'


urlpatterns = [
    path('', views.PostListView.as_view(), name="home"),
    path('post/<slug:post_slug>/', views.PostDetailView.as_view(), name="post_detail"),
    path("category/<slug:cat_slug>/", views.PostCategoryListView.as_view(), name="category_detail"),
    path("tag/<slug:tag_slug>/", views.PostTagsListView.as_view(), name="tag_detail"),
    path("add_post/", views.PostCreateView.as_view(), name="add_post"),
    path('edit/<slug:slug>/', views.PostUpdateView.as_view(), name="update_post"),
    path("post/<slug:post_slug>/comment/", views.AddCommentView.as_view(), name="add_comment"),
    path("comment/<int:comment_id>/delete/", views.AddCommentView.as_view(), name="comment_delete"),
    path('post/<slug:post_slug>/comment/<int:comment_id>/edit/', views.CommentUpdateView.as_view(), name="edit_comment"),
    path("recomendation/", views.RecomendationListView.as_view(), name="recomendations"),
    path("search_post/", views.search_posts, name="search_post"),
    path("post/<slug:post_slug>/like/", views.like_post, name="like_post"),
    
    path('notifications/', views.NotificationListView.as_view(), name="notifications_list"),
    path('read/<int:notification_id>/', views.mark_notification_as_read, name="mark_notification_as_read"),
    path("about/", views.about, name='about'),
    path("contact/", views.contact, name="contact"),
]
