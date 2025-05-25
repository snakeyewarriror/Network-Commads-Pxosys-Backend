from django.urls import path, include

from . import views
from .views import CreateUserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('', views.home , name = 'home'),
    # path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', CreateUserView.as_view() , name = 'register'),
    path('token/', TokenObtainPairView.as_view() , name = 'get_token'),
    path('refresh/', TokenRefreshView.as_view() , name = 'refresh'),
    path('api-auth/', include("rest_framework.urls")),
]
