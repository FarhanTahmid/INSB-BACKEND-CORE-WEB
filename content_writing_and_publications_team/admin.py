from django.contrib import admin
from .models import Content_Team_Document,Content_Caption
# Register your models here.

@admin.register(Content_Team_Document)
class Content_Team_Document(admin.ModelAdmin):
    list_display = ['event_id','document']

@admin.register(Content_Caption)
class Content_Caption(admin.ModelAdmin):
    list_display = ['event_id','caption']