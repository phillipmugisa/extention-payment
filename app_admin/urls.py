from django.urls import path
from app_admin import views

app_name = "app_admin"

urlpatterns = [
    path("", views.AdminManagersView.as_view(), name="home"),
    path("subscriptions/", views.AdminSubscriptionListView.as_view(), name="subscriptions"),
    path("users/", views.AdminUserListView.as_view(), name="users"),
    path("services/", views.AdminServiceListView.as_view(), name="services"),
    path("features/create/", views.FeatureCreateView.as_view(), name="features-create"),

    path("pricings/", views.AdminPricingListView.as_view(), name="pricings"),
    path("pricing/create/", views.PricingCreateView.as_view(), name="pricing-create"),
]
