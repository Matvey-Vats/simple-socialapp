from django.urls import path

from . import views


# app_name = 'posts'


urlpatterns = [
    path('', views.PostListView.as_view(), name="home"),
    path('post/<slug:post_slug>/', views.PostDetailView.as_view(), name="post_detail"),
    path("category/<slug:cat_slug>/", views.PostCategoryListView.as_view(), name="category_detail"),
    path("tag/<slug:tag_slug>/", views.PostTagsListView.as_view(), name="tag_detail"),
    path("add_post/", views.PostCreateView.as_view(), name="add_post"),
    path("post/<slug:post_slug>/comment/", views.AddCommentView.as_view(), name="add_comment"),
    path("comment/<int:comment_id>/delete/", views.AddCommentView.as_view(), name="comment_delete"),
    path('post/<slug:post_slug>/comment/<int:comment_id>/edit/', views.CommentUpdateView.as_view(), name="edit_comment"),
    path("about/", views.about, name='about'),
    path("contact/", views.contact, name="contact"),
]
