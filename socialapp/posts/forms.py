from django import forms

from .models import Post, Category, Comment

class AddPageForm(forms.ModelForm):
    # category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Категория", empty_label="Категория не выбрана")
    class Meta:
        model = Post
        fields = ['photo', 'title', 'content', 'tags', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={"class": 'form-input', "placeholder": 'Заголовок'}),
            'content': forms.Textarea(attrs={'cols': 150, 'row': 5, 'placeholder': "Контент"}),
        }
        
        
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) > 50:
            raise forms.ValidationError("Заголовок не может превышать 50 символов")
        return title
class CommentCreateForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ['content']
        
        
    def clean_content(self):
        content = self.cleaned_data['content']
        if len(content) > 300:
            raise forms.ValidationError("Комментарий не может превышать 300 символов")
        return content