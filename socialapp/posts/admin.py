from django.contrib import admin


from .models import Post, Category, TagPost, Comment
# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'is_published']
    list_display_links = ['title']
    list_editable = ['is_published']
    list_per_page = 5
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ['title', 'category__name']
    list_filter = ['category__name', 'is_published']
    
    save_on_top = True
    
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
@admin.register(TagPost)
class TagPostAdmin(admin.ModelAdmin):
    list_display = ['tag', 'slug']
    prepopulated_fields = {'slug': ('tag',)}
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post']
    
