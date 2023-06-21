from django.urls import path, include
from knox import views as knox_views

from .views import LoginAPI, RegistrationAPI, ResetPasswordView, UserAPI

urlpatterns = [
    path('auth/register/', RegistrationAPI.as_view()),
    path('auth/login/', LoginAPI.as_view()),
    path('auth/user/', UserAPI.as_view()),
    path('auth/change-password/', ResetPasswordView.as_view()),
    path('auth/reset-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout')
]
