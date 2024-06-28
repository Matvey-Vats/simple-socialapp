from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path('registration/', views.RegisterUser.as_view(), name="registration"),
    path("profile/", views.ProfileUserView.as_view(), name="profile"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    
    path("profile/<str:username>/", views.UserProfileView.as_view(), name="user_profile"),
    path('subscribe/<str:username>/', views.subscribe, name='subscribe'),
    path('unsubscribe/<str:username>/', views.unsubscribe, name='unsubscribe'),
    
    path("subscribers/<str:username>/", views.UserSubscribersView.as_view(), name="subscribers_list"),
    path("subscriptions/<str:username>/", views.UserSubscriptionsView.as_view(), name="subscriptions_list"),
    
    path("my_posts/", views.MyPostListView.as_view(), name="my_posts"),
    path("favorite_posts/", views.FavoriteListView.as_view(), name="favorite_posts"),
    path("my_comments/", views.CommentsListView.as_view(), name="my_comments"),
]
