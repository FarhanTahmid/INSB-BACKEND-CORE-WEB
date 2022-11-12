from django.db import models
from django.urls import reverse

# Create your models here.
class recruitment_session(models.Model):
    session=models.CharField(null=False,blank=False,max_length=100)
    
    class Meta:
        verbose_name="Recruitment Session"
    def __str__(self) -> str:
        return self.session
    def get_absolute_url(self):
        return reverse("session", kwargs={"session":self.session})

class recruited_members(models.Model):
    nsu_id=models.IntegerField(primary_key=True,blank=False,null=False)
    first_name=models.CharField(null=True,blank=True,max_length=50)
    middle_name=models.CharField(null=True,blank=True,max_length=50)
    last_name=models.CharField(null=True,blank=True,max_length=50)
       
    