from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
    email = forms.EmailField(max_length=200)
    name = forms.CharField(max_length=200)
    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'password1', 'password2')

class LoginUserForm(AuthenticationForm):
    pass