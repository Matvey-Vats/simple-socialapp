from .utils import menu
from django.conf import settings

def get_post_context(request):
    return {"mainmenu": menu}

def get_default_user_img(request):
    return {"default_img": settings.DEFAULT_USER_IMAGE}