from typing import Iterable
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.validators import MaxLengthValidator


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


class PublishedManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_published=Post.Status.PUBLISHED)
    
    
class Post(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, "Черновик"
        PUBLISHED = 1, "Опубликовать"
        
    title = models.CharField(max_length=125)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    photo = models.ImageField(upload_to="photos/%Y/%m/%d", default=None, blank=True, null=True, verbose_name="Photo")
    content = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)), default=Status.PUBLISHED)
    category = models.ForeignKey(to="Category", on_delete=models.PROTECT, related_name="posts", null=True, blank=True)
    tags = models.ManyToManyField("TagPost", blank=True, related_name="tags")
    likes = models.ManyToManyField(get_user_model(), related_name="likes_posts", blank=True)
    
    
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True)
    
    published = PublishedManager()
    objects = models.Manager()
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def image_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url
        
    def total_likes(self):
        return self.likes.count()
    
    class Meta:
        ordering = ["-time_create"]
        indexes = [
            models.Index(fields=['-time_create'])
        ]
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        
    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"post_slug": self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_cyrillic(self.title)
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super(Post, self).save(*args, **kwargs)
        
        
    
class Category(models.Model):
    name = models.CharField(max_length=125, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"cat_slug": self.slug})
    
    
class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, db_index=True, unique=True)
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
    
    def __str__(self) -> str:
        return self.tag
    
    def get_absolute_url(self):
        return reverse("tag_detail", kwargs={"tag_slug": self.slug})
    
    

class Comment(models.Model):
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(to="Post", on_delete=models.CASCADE, related_name="comments")
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
        

class Notification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="notifications")
    text = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"Notifications for {self.user.username}: {self.text}"
    