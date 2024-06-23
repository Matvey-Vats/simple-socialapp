from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path('registration/', views.RegisterUser.as_view(), name="registration"),
    path("profile/", views.ProfileUserView.as_view(), name="profile"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
