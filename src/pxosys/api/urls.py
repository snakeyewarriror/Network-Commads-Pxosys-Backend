from rest_framework.routers import DefaultRouter
from commands.urls import default_router_commands
from django.urls import path, include


router = DefaultRouter()

router.registry.extend(default_router_commands.registry)


urlpatterns =  [
    path('', include(router.urls)),
]