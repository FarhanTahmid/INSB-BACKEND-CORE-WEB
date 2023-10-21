from django.urls import path
from . import views

app_name="ieee_nsu_sb_ras_sbc"

urlpatterns = [
    path('',views.Homepage,name="homepage")
]
