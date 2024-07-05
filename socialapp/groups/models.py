from django.db import models
from django.contrib.auth import get_user_model
from posts.models import TagPost
from django.utils.text import slugify
from django.core.validators import MaxLengthValidator
from django.urls import reverse




TRANSLIT_DICT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
    'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
    'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'J', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
    'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh',
    'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E',
    'Ю': 'Yu', 'Я': 'Ya'
}
# Create your models here.
def slugify_cyrillic(text):
    transliterated_text = ''.join(TRANSLIT_DICT.get(c, c) for c in text)
    return slugify(transliterated_text)





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
        return reverse("groups:group_detail", kwargs={"group_slug": self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_cyrillic(self.name)
            original_slug = self.slug
            counter = 1
            while Group.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super(Group, self).save(*args, **kwargs)
    
    
class GroupMembership(models.Model):
    group = models.ForeignKey(Group, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), related_name="memberships", on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.user.username} in {self.group.name}"
    

class GroupPost(models.Model):
    group = models.ForeignKey(Group, related_name="group_posts", on_delete=models.CASCADE)
    author = models.ForeignKey(get_user_model(), related_name="group_posts", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True)
    photo = models.ImageField(upload_to="group_posts/", blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(TagPost, blank=True, related_name="posts")
    likes = models.ManyToManyField(get_user_model(), related_name="liked_group_posts", blank=True)
    
    
    def __str__(self) -> str:
        return self.title
    
    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"group_slug": self.group.slug,
                                                    "post_slug": self.slug,})
    def total_likes(self):
        return self.likes.count()
    
    @property
    def image_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_cyrillic(self.title)
            original_slug = self.slug
            counter = 1
            while GroupPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super(GroupPost, self).save(*args, **kwargs)
    
    
class GroupComment(models.Model):
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name="group_comments")
    post = models.ForeignKey(to="GroupPost", on_delete=models.CASCADE, related_name="group_comments")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    content = models.TextField(max_length=300, validators=[MaxLengthValidator(300)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"] 
        verbose_name = "Коментарий"
        verbose_name_plural = "Коментарии"
        
        
    def __str__(self) -> str:
        return f"Коментарий от {self.user.username} на {self.post.title}"
    
    
    @property
    def is_reply(self):
        return self.parent is not None
        