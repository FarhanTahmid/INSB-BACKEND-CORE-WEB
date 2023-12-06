from django.db import models
from django.urls import reverse
# Create your models here.

# Event Category Table
class Event_Categories(models.Model):
    event_category=models.CharField(null=False,blank=False,max_length=60)
    
    class Meta:
        verbose_name="Event Category"
    
    def __str__(self) -> str:
        return str(self.pk)

class SuperEvents(models.Model):
    super_event_name=models.CharField(null=False,blank=False,max_length=150)
    super_event_description=models.CharField(null=True,blank=True,max_length=500)
    start_date=models.DateField(null=True,blank=True,auto_now_add=False)
    end_date=models.DateField(null=True,blank=True,auto_now_add=False)

    class Meta:
        verbose_name="Super Event"
    def __str__(self) -> str:
        return self.super_event_name
    def get_absolute_url(self):
        return reverse("super_event", kwargs={"event_name": self.super_event_name})
