from django.contrib import admin
from . models import Teams,Roles_and_Position
# Register your models here.
@admin.register(Teams)
class Teams(admin.ModelAdmin):
    list_display=['id','team_name']
@admin.register(Roles_and_Position)
class Roles(admin.ModelAdmin):
    list_display= ['id','role']