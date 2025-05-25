from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

default_router_commands = DefaultRouter()

default_router_commands.register(r'vendors', views.AdminVendorViewSet, basename='vendors')
default_router_commands.register(r'os', views.AdminOSViewSet, basename='os')
default_router_commands.register(r'categories', views.AdminCategoryViewSet, basename='categories')
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


    # --- OS Paths ---
    # Allow any authenticated user to create an OS
    path('os/create/', views.OSCreateAPIView.as_view(), name='os-create'),
    
    # List OSes created by the current user
    path('os/my-list/', views.UserOSListSet.as_view(), name='user-os-list'),
    # List all OSes
    path('os/get-all/', views.OSListSet.as_view(), name='os-list'),
    
    # Delete a specific OS created by the current user (needs primary key)
    path('os/my-delete/<int:pk>/', views.UserOSDelete.as_view(), name='user-os-delete'),


    # --- Category Paths ---
    # Allow any authenticated user to create a Category
    path('categories/create/', views.CategoryCreateAPIView.as_view(), name='category-create'),
    
    # List Categories created by the current user
    path('categories/my-list/', views.UserCategoryListSet.as_view(), name='user-category-list'),
    # List all Categories
    path('categories/get-all/', views.CategoryListSet.as_view(), name='category-list'),
    # List all Categories
    path('categories/get-all-tree/', views.CategoryTreeListSet.as_view(), name='category-list-tree'),
    
    # Delete a specific Category created by the current user (needs primary key)
    path('categories/my-delete/<int:pk>/', views.UserCategoryDelete.as_view(), name='user-category-delete'),


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
