from django.db import models
from central_events.models import Events
from django_resized import ResizedImageField
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files import File

# Create your models here.
#Table for Media Links and Images
class Graphics_Link(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    graphics_link=models.URLField(null=True,blank=True,max_length=300)
class Graphics_Banner_Image(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    selected_image=ResizedImageField(null=True,blank=True,default=None,upload_to='Event_Banner_Image/')

class Graphics_Form_Link(models.Model):
    event_id = models.ForeignKey(Events,on_delete=models.CASCADE)
    graphics_form_link_name = models.CharField(null=True,blank=True,max_length = 200)
    graphics_form_link = models.URLField(null=True,blank=True,max_length=300)