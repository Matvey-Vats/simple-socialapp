from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from socialapp import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls')),
    path('users/', include("users.urls", namespace="users")),
    path("groups/", include("groups.urls", namespace="groups")),
    path("__debug__/", include("debug_toolbar.urls")),
    
    path('api/', include('posts.api.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    