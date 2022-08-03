from django.contrib import admin
from django.urls import path, include
from manager.views import HomePageView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("manager.urls", namespace="manager")),
    path('api/', include('api.urls', namespace='api')),
    path("auth/", include("app_auth.urls", namespace="app_auth")),
    path("accounts/profile/", HomePageView.as_view()),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
