from django.contrib import admin
from . models import Logistic_Item_List


# Register your models here.
@admin.register(Logistic_Item_List)
class Logistic_Item(admin.ModelAdmin):
    list_display=['id']