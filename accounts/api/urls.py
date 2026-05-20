from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.api.views import LoginView, RegisterView, MeView

urlpatterns = [
    path('api/token/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
]