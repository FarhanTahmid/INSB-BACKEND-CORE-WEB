from django.db import models
from central_events.models import Events
from django_resized import ResizedImageField
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files import File

# Create your models here.
#Table for Media Links and Images
class Media_Link(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    media_link=models.URLField(null=True,blank=True,max_length=300)
    logo_link = models.URLField(null=True,blank=True,max_length=300)
class Media_Images(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    selected_images=models.ImageField(null=True,blank=True,default=None,upload_to='Event Selected Images/')

    def _process_image(self, image_field):
        if image_field:
            img = Image.open(BytesIO(image_field.read()))

            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif:
                    for tag, label in ExifTags.TAGS.items():
                        if label == 'Orientation':
                            orientation = tag
                            break
                    if orientation in exif:
                        if exif[orientation] == 3:
                            img = img.rotate(180, expand=True)
                        elif exif[orientation] == 6:
                            img = img.rotate(270, expand=True)
                        elif exif[orientation] == 8:
                            img = img.rotate(90, expand=True)

            img.thumbnail((1080, 1080), Image.ANTIALIAS)
            output = BytesIO()
            img.save(output, format=img.format, quality=85)
            output.seek(0)
            setattr(self, image_field.name, File(output, image_field))

    def save(self, *args, **kwargs):

        # Process the background_image
        self._process_image(self.selected_images)
         # Process other image fields as needed
        # Example: self._process_image(self.mission_picture)
        #          self._process_image(self.vision_picture)

        return super().save(*args, **kwargs) 


