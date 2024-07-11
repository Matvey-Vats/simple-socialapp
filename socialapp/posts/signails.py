from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Post, Notification


@receiver(post_save, sender=Post)
def create_post_like_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.author,
            text=f"Ваш пост '{instance.title}' был создан"
        )
        
        
@receiver(m2m_changed, sender=Post.likes.through)
def create_like_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for pk in pk_set:
            user = get_user_model().objects.get(pk=pk)
            Notification.objects.create(
                user=instance.author,
                text=f"Пользователь {user.username} поставил лайк вашему посту {instance.title}"
            )
            
            
