from django.urls import path
from . import views


urlpatterns = [
    path('dashboard', views.dashboard, name ='user-dashboard'),
    path('update-user/', views.update_user, name ='update-user'),
    path('delete-account-user/', views.delete_account_user, name ='delete-account-user'),
    path('password-update-user/', views.password_update_user, name ='password-update-user'),
]
