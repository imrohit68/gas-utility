from django.urls import path
from .views import register_user, login_user, get_user_profile, ping_pong

urlpatterns = [
    path("auth/register/", register_user, name="register"),
    path("auth/login/", login_user, name="login"),
    path("profile/", get_user_profile, name="profile"),
    path("ping/", ping_pong, name="ping_pong"),
]
