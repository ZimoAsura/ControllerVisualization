from django.contrib import admin

# Register your models here.
from .models import controller_data, controller_file

admin.site.register(controller_data)
admin.site.register(controller_file)
