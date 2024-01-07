from django.contrib import admin
from .models import SC_AG_Members,SC_AG_FeedBack
# Register your models here.
@admin.register(SC_AG_Members)
class SC_AG_Members(admin.ModelAdmin):
    list_display=['id','sc_ag','member','team','position']

@admin.register(SC_AG_FeedBack)
class SC_AG_FeedBack(admin.ModelAdmin):

    list_display = ['society','date','name','email','message','is_responded']
