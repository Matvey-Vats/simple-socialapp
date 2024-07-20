from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostAPIList, CommentAPIList, TagPostApiList

from . import views

router = DefaultRouter()
router.register(r'posts', PostAPIList)
router.register(r'comments', CommentAPIList)
router.register(r'tags', TagPostApiList)

urlpatterns = [
    path('', include(router.urls)),
    # path('posts/', views.PostAPIList.as_view(), name="post_list"),
    # path('posts/<int:pk>/', views.PostUpdateAPIView.as_view(), name="post_detail"),
    # path('posts/delete/<int:pk>/', views.PostDetailAPIView.as_view(), name="post_delete"),
    # path('posts/', views.PostAPIList.as_view(), name="post-list"),
]
