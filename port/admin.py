from django.contrib import admin
from . models import Teams
# Register your models here.
@admin.register(Teams)
class Teams(admin.ModelAdmin):
    list_display=['id','team_name']