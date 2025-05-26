from django.urls import path, include

from .views import CreateUserView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', CreateUserView.as_view() , name = 'register'),
    path('token/', CustomTokenObtainPairView.as_view() , name = 'get_token'),
    path('refresh/', TokenRefreshView.as_view() , name = 'refresh'),
    path('api-auth/', include("rest_framework.urls")),
]
