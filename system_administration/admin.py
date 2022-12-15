from django.contrib import admin
from . models import adminUsers
# Register your models here.
@admin.register(adminUsers)
class Admin(admin.ModelAdmin):
    list_display=['username','name','email']