from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from user.views import RegisterView, EmailTokenObtainPairView, UserDetailView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register_user"),
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", UserDetailView.as_view(), name="me"),
]

app_name = "user"
