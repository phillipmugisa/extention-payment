from django.urls import path
from app_auth import views

app_name = "app_auth"

urlpatterns = [
    path("login/", views.loginUserView.as_view(), name="login"),
    path("login/<str:usertype>/", views.loginUserView.as_view(), name="login_extension"),
    path("complete/<str:source>", views.login_complete, name="login_complete"),
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path("logout/", views.logout, name="logout"),
]
