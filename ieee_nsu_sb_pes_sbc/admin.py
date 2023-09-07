from django.contrib import admin
from .models import PesMembers
# Register your models here.

@admin.register(PesMembers)
class PesMembers(admin.ModelAdmin):
    list_display=[
        'id','ieee_id','position','team'
    ]