from django.urls import path

from . import views

app_name = "groups"

urlpatterns = [
    path('', views.GroupListView.as_view(), name="group_list"),
    path('group/<slug:group_slug>/', views.GroupDetailView.as_view(), name="group_detail"),
]
