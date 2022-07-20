from django.urls import path
from app_auth import views

app_name = 'app_auth'

urlpatterns = [
    path('login/', views.loginUserView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
]