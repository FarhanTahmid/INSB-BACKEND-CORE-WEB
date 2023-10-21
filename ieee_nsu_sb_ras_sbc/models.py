from django.db import models
from django_resized import ResizedImageField
# Create your models here.

# RAS SBC
class Ras_Sbc(models.Model):
    ras_banner_image=ResizedImageField(upload_to='main_website_files/RAS/banner_picture')
    about_ras=models.TextField(null=False,blank=False,max_length=1000)
    mission_vision=models.TextField(null=False,blank=False,max_length=1000)
    mission_vision_picture=ResizedImageField(upload_to='main_website_files/RAS/mission_vision_picture')
    what_is_ras=models.TextField(null=True,blank=True,max_length=300)
    why_join_ras=models.TextField(null=True,blank=True,max_length=300)
    what_activities=models.TextField(null=True,blank=True,max_length=300)
    how_to_join=models.TextField(null=True,blank=True,max_length=300)
    
    class Meta:
        verbose_name="RAS SBC Informations"
    
    def __str__(self) -> str:
        return str(self.pk)