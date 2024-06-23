from django import forms

from .models import Post, Category, Comment

class AddPageForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Категория", empty_label="Категория не выбрана")
    class Meta:
        model = Post
        fields = ('title', 'content', 'photo', 'category', 'tags')
        widgets = {
            'title': forms.TextInput(attrs={"class": 'form-input', "placeholder": 'Заголовок'}),
            'content': forms.Textarea(attrs={'cols': 150, 'row': 5}),
        }
        
class CommentCreateForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ['content']