from django.contrib import admin
from .models import Manage_Team

# Register your models here.
@admin.register(Manage_Team)
class Manage_Team(admin.ModelAdmin):
    list_display = ['ieee_id','manage_team_access']

