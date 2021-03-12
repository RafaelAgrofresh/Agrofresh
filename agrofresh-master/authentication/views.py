from . import forms # LoginForm, SignUpForm, UserCreationForm
from django.contrib.auth import authenticate, login, mixins
from django.contrib.auth.models import User, Group
from django.forms.utils import ErrorList
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView


def login_view(request):
    form = forms.LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "login.html", {"form": form, "msg" : msg})


def register_user(request):
    form    = form.SignUpForm(request.POST or None)
    msg     = None
    success = False

    if request.method == "POST":
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            msg     = 'User created - please <a href="/login">login</a>.'
            success = True
            #return redirect("/login/")
        else:
            msg = 'Form is not valid'

    return render(request, "register.html", { "form": form, "msg" : msg, "success" : success })


# mixins.PermissionRequiredMixin -> permission_required = 'authentication.create_user'
# mixins.UserPassesTestMixin

class UserCreationFormView(mixins.UserPassesTestMixin, FormView):
    form_class = forms.UserCreationForm
    template_name = "create_user_form.html"
    success_url = "/"

    def test_func(self):
        user = self.request.user
        return (
            user.is_staff
            or user.groups.filter(name__iexact='nivel3').exists()
        )

    def form_valid(self, form):
        group = form.cleaned_data.get('group')
        if not isinstance(group, Group):
            raise Exception(f"Expecte one group")

        user = User.objects.create_user(
            username=form.cleaned_data.get('username'),
            email=form.cleaned_data.get('email'),
            password=form.cleaned_data.get('password1'))

        user.groups.add(group)

        return super().form_valid(form)
