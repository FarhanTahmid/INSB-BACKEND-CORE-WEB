from django.contrib import admin

# Register your models here.

from .models import Ras_Query_Form
@admin.register(Ras_Query_Form)
class QueryForm(admin.ModelAdmin):
    list_display=['pk','name','email']
