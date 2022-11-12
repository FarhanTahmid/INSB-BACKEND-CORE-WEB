from django.contrib import admin
from . models import recruitment_session
# Register your models here.

@admin.register(recruitment_session)
class Session(admin.ModelAdmin):
    list_display= ['id','session']
