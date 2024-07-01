from django.contrib import admin
from .models import Group, GroupMembership, GroupPost
# Register your models here.

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('name',)}

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    pass

@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    
    