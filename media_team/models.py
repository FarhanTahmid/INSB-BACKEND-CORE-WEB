from django.db import models
# from central_branch.models import Events
from django_resized import ResizedImageField

# Create your models here.
#Table for Media Links and Images
# class Media_Link(models.Model):
#     event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
#     media_link=models.URLField(null=True,blank=True,max_length=300)
#     logo_link = models.URLField(null=True,blank=True,max_length=300)
# class Media_Images(models.Model):
#     event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
#     selected_images=ResizedImageField(null=True,blank=True,default=None,upload_to='Event Selected Images/')


