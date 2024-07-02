from django.db import models
from django.contrib.auth import get_user_model
from posts.models import TagPost
from django.urls import reverse

# Create your models here.
class Group(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        SECRET = "secret", "Secret"
        
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="group_covers/", null=True, blank=True)
    privacy = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(get_user_model(), related_name="owned_groups", on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.name
    
    
    def get_absolute_url(self):
        return reverse("group_detail", kwargs={"group_slug": self.slug})
    
    
    
class GroupMembership(models.Model):
    group = models.ForeignKey(Group, related_name="memberhips", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), related_name="memberships", on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.user.username} in {self.group.name}"
    

class GroupPost(models.Model):
    group = models.ForeignKey(Group, related_name="posts", on_delete=models.CASCADE)
    author = models.ForeignKey(get_user_model(), related_name="group_posts", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    photo = models.ImageField(upload_to="group_posts/", blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(TagPost, blank=True, related_name="posts")
    likes = models.ManyToManyField(GroupMembership, related_name="likes_posts", blank=True)
    
    
    def __str__(self) -> str:
        return self.title
    
    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"group_slug": self.group.slug,
                                                    "post_slug": self.slug,})
    