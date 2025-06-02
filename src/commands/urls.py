from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

default_router_commands = DefaultRouter()

default_router_commands.register(r'vendors', views.AdminVendorViewSet, basename='vendors')
default_router_commands.register(r'platform', views.AdminOSViewSet, basename='platform')
default_router_commands.register(r'tags', views.AdminTagViewSet, basename='tags')
default_router_commands.register(r'commands-admin', views.AdminCommandViewSet, basename='commands')


urlpatterns = [
    
    # --- Vendor Paths ---
    # Allow any authenticated user to create a vendor
    path('vendors/create/', views.VendorCreateAPIView.as_view(), name='vendor-create'),
    
    # List vendors created by the current user
    path('vendors/my-list/', views.UserVendorListSet.as_view(), name='user-vendor-list'),
    # List all vendors
    path('vendors/get-all/', views.VendorListSet.as_view(), name='vendor-list'),
    
    # Delete a specific vendor created by the current user (needs primary key)
    path('vendors/my-delete/<int:pk>/', views.UserVendorDelete.as_view(), name='user-vendor-delete'),


    # --- Platform Paths ---
    # Allow any authenticated user to create an Platform
    path('platform/create/', views.OSCreateAPIView.as_view(), name='platform-create'),
    
    # List Platforms created by the current user
    path('platform/my-list/', views.UserOSListSet.as_view(), name='user-platform-list'),
    # List all Platforms
    path('platform/get-all/', views.OSListSet.as_view(), name='platform-list'),
    
    # Delete a specific Platform created by the current user (needs primary key)
    path('platform/my-delete/<int:pk>/', views.UserOSDelete.as_view(), name='user-platform-delete'),


    # --- Tag Paths ---
    # Allow any authenticated user to create a Tag
    path('tags/create/', views.TagCreateAPIView.as_view(), name='tag-create'),
    
    # List Tags created by the current user
    path('tags/my-list/', views.UserTagListSet.as_view(), name='user-tag-list'),
    # List all Tags
    path('tags/get-all/', views.TagListSet.as_view(), name='tag-list'),
    # List all Tags
    path('tags/get-all-tree/', views.TagTreeListSet.as_view(), name='tag-list-tree'),
    
    # Delete a specific Tag created by the current user (needs primary key)
    path('tags/my-delete/<int:pk>/', views.UserTagDelete.as_view(), name='user-tag-delete'),


    # --- Command Paths ---
    
    # Allow any authenticated user to create a Command
    path('commands/create/', views.CommandCreateAPIView.as_view(), name='command-create'),
    # Allow any authenticated user to upload a CSV of commands
    path('commands/csv-upload', views.CommandCSVUploadView.as_view() , name = 'csv-upload'),
    
    # List Commands created by the current user
    path('commands/my-list/', views.UserCommandListSet.as_view(), name='user-command-list'),
    # List all Commands
    path('commands/get-all/', views.CommandListSet.as_view(), name='command-list'),
    # List all Commands with filtering options
    path('commands/get-filtered/', views.CommandFilteredListView.as_view(), name='command-list-filtered'),
    
    # Delete a specific Command created by the current user (needs primary key)
    path('commands/my-delete/<int:pk>/', views.UserCommandDelete.as_view(), name='user-command-delete'),

]
