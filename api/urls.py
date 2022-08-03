from django.urls import path
from api.views import AliExpressSubcriptionRetrieveView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


app_name = 'api'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('subscriptions/aliexpress/', AliExpressSubcriptionRetrieveView.as_view(), name='subscriptions')
]