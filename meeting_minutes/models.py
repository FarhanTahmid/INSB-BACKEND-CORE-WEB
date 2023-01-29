from django.db import models
from django.urls import reverse
# Create your models here.

# meeting minutes' information
class meeting_minute(models.Model):
    meeting_title=models.CharField(null=False,blank=False,max_length=150)
    meeting_date=models.DateField(null=True,blank=True,auto_now_add=False)
    meeting_venue=models.CharField(null=False,blank=False,max_length=150)
    meeting_present=models.CharField(null=False,blank=False,max_length=150)
    meeting_excused=models.CharField(null=False,blank=False,max_length=150)
    meeting_absent=models.CharField(null=False,blank=False,max_length=150)
    meeting_called_by=models.CharField(null=False,blank=False,max_length=150)
    meeting_agendas=models.CharField(null=False,blank=False,max_length=150)
    meeting_approval=models.CharField(null=False,blank=False,max_length=150)
    meeting_discussion=models.CharField(null=False,blank=False,max_length=3000)
#team foreign key from each chapters
    class Meta:
        verbose_name="Registered Meetings"
    
    def __str__(self) -> str:
        return self.meeting_title
    def get_absolute_url(self):
        return reverse("Registered Meetings", kwargs={"meeting_title": self.meeting_title})
