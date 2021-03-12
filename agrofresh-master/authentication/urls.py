from django.urls import include, path
from .views import login_view, register_user, UserCreationFormView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('create_user/', UserCreationFormView.as_view(), name="create_user"),
]
