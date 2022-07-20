from django.urls import path
from manager import views
from django.views.generic import TemplateView

app_name = 'manager'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='dashboard'),
    path('package/<str:slug>', views.PackageDetailView.as_view(), name='package'),
]