from django import forms
from django.contrib.auth import get_user_model, forms as auth_forms
from django.contrib.auth.models import Group


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",
                "class": "form-control"
            }
        ))

class SignUpForm(auth_forms.UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder" : "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password check",
                "class": "form-control"
            }
        ))

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')


class UserCreationForm(auth_forms.UserCreationForm):
    group = forms.ModelChoiceField(
        required=True,
        queryset=Group.objects.filter(name__in=("Nivel1","Nivel2","Nivel3"))
    )
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2', 'group')