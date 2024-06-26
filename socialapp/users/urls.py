from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path('registration/', views.RegisterUser.as_view(), name="registration"),
    path("profile/", views.ProfileUserView.as_view(), name="profile"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    
    path("my_posts/", views.MyPostListView.as_view(), name="my_posts"),
    path("favorite_posts/", views.FavoriteListView.as_view(), name="favorite_posts"),
    path("my_comments/", views.CommentsListView.as_view(), name="my_comments"),
]
