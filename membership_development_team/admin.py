from django.contrib import admin
from . models import Renewal_Sessions
# Register your models here.
@admin.register(Renewal_Sessions)
class Renewal_Sessions(admin.ModelAdmin):
    list_display=['id','session_name','session_time']