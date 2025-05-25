from django.contrib import admin

from .models import *


admin.site.register(Commands)
admin.site.register(Vendor)  # If you want to manage vendors in the admin as well
admin.site.register(OS)  # If you want to manage OS in the admin
admin.site.register(Category)  # If you want to manage categories in the admin
