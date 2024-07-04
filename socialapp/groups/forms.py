from django import forms
from .models import GroupComment

class CommentCreateForm(forms.ModelForm):
    
    class Meta:
        model = GroupComment
        fields = ['content']
        
        
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) > 300:
            raise forms.ValidationError("Комментарий не может превышать 300 символов")
        return content