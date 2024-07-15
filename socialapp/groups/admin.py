from django.contrib import admin
from .models import Group, GroupMembership, GroupPost, GroupComment
# Register your models here.

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'privacy', 'owner']
    prepopulated_fields = {"slug": ('name',)}
    list_editable = ["privacy"]

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'is_admin']

@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    list_display = ['title', 'slug', 'group', 'author', 'total_likes']
    list_per_page = 10
    
    
@admin.register(GroupComment)
class GroupCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'content', 'parent']