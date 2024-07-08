from django import forms
from .models import GroupComment, Group, GroupPost, GroupMembership
from django.db.models import Q

class CommentCreateForm(forms.ModelForm):
    
    class Meta:
        model = GroupComment
        fields = ['content']
        
        
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) > 300:
            raise forms.ValidationError("Комментарий не может превышать 300 символов")
        return content
    
class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'cover_image', 'privacy']
        widgets = {
            'name': forms.TextInput(attrs={"placeholder": "Заголовок"}),
            'description': forms.Textarea(attrs={"placeholder": "Описание"}),
        }
        
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) > 30:
            raise forms.ValidationError("Заголовок не может превышать 30 символов")
        return name
    
class GroupPostWithGroupForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ['group', 'title', 'content', 'photo', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={"placeholder": "Заголовок"}),
            'content': forms.Textarea(attrs={"placeholder": "Контент"}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['group'].queryset = Group.objects.filter(
                Q(memberships__user=user) | Q(owner=user)
            ).distinct()
            self.fields['group'].empty_label="Выберите группу"
        
class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ['title', 'content', 'photo', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={"placeholder": "Заголовок"}),
            'content': forms.Textarea(attrs={"placeholder": "Контент"})
        }