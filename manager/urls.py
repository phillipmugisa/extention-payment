from django.urls import path
from manager import views
from django.views.generic import TemplateView

app_name = 'manager'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='dashboard'),
    path('package/<str:slug>', views.PackageDetailView.as_view(), name='package'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('complete-payment/', views.CompletePaymentView.as_view(), name='complete-payment'),
]