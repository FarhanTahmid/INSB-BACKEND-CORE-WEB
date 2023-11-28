from django.contrib import admin
from .models import SC_AG_Members
# Register your models here.
@admin.register(SC_AG_Members)
class SC_AG_Members(admin.ModelAdmin):
    list_display=['id','sc_ag','member','team','position']
