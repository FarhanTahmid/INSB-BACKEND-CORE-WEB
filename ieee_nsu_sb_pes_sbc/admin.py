from django.contrib import admin
from .models import PesMembers,PesDataAccess
# Register your models here.

@admin.register(PesMembers)
class PesMembers(admin.ModelAdmin):
    list_display=[
        'id','ieee_id','position','team'
    ]

@admin.register(PesDataAccess)
class PesDataAccess(admin.ModelAdmin):
    list_display=[
        'ieee_id','renewal_data_access'
    ]