from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

import datetime

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Имя пользователя"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}))
    class Meta:
        model = User
        fields = ['username', 'password']
        
        
class RegistrationUserForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Повтор пароля",}))
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Имя пользователя"}),
            "email": forms.TextInput(attrs={"placeholder": "E-mail",}),
            "first_name": forms.TextInput(attrs={"placeholder": "Имя",}),
            "last_name": forms.TextInput(attrs={"placeholder": "Фамилия",}),
        }
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует")
        return email
    
class UserProfileForm(forms.ModelForm):
    username = forms.CharField(disabled=True, widget=forms.TextInput(attrs={"placeholder": "Username",}))
    email = forms.CharField(disabled=True, widget=forms.TextInput(attrs={"placeholder": "E-mail",}))
    this_year = datetime.date.today().year
    date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year-100, this_year-5))))
    
    class Meta:
        model = User
        fields = ['photo', 'username', 'email', 'date_birth', 'first_name', 'last_name']
        
        widgets = {
            'first_name': forms.TextInput(attrs={"placeholder": "Имя"}),
            'last_name': forms.TextInput(attrs={"placeholder": "Фамилия"}),
        }