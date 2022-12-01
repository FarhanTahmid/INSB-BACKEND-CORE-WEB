from django.db import models
from django.urls import reverse

# Create your models here.

#The events table. Primary key is the id
class Events(models.Model):
    event_name=models.CharField(null=False,blank=False,max_length=150)
    event_description=models.CharField(null=True,blank=True,max_length=500)
    probable_date=models.DateField(null=True,blank=True,auto_now_add=False)
    collaboration_with=models.CharField(null=True,blank=True,max_length=100)
    final_date=models.DateField(null=True,blank=True,auto_now_add=False)
    class Meta:
        verbose_name="Registered Events"
    
    def __str__(self) -> str:
        return self.event_name
    def get_absolute_url(self):
        return reverse("registered_events", kwargs={"event_name": self.event_name})
    