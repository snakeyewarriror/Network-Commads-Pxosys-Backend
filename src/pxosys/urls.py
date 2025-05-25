from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('commands.urls')),
    path('', include('account.urls')),
    path('user/', include('user.urls')),
    path('commands/', include('pxosys.api.urls')),
]
