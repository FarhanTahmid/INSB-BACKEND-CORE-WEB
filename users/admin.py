from django.contrib import admin
from . models import Members
# Register your models here.
@admin.register(Members)
class Members(admin.ModelAdmin):
    list_display=['ieee_id','name','email_ieee']