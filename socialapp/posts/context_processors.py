from .utils import menu
from django.conf import settings
from .models import Notification

def get_post_context(request):
    return {"mainmenu": menu}

def get_default_user_img(request):
    return {"default_img": settings.DEFAULT_USER_IMAGE}


def unread_notifications_count(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        unread_count = 0
    return {"unread_notifications_count": unread_count}