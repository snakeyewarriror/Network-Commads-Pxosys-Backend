from django.contrib import admin

from .models import *


admin.site.register(Commands)
admin.site.register(Vendor)  # If you want to manage vendors in the admin as well
admin.site.register(Platform)  # If you want to manage Platform in the admin
admin.site.register(Tag)  # If you want to manage tags in the admin
