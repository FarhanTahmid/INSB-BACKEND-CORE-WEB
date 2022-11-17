from django.db import models
from django.urls import reverse
from insb_port import settings

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
    contact_no=models.CharField(null=True,blank=True,max_length=15)
    date_of_birth=models.DateField(null=True,blank=True)
    email_personal=models.EmailField(null=True,blank=True,max_length=50)
    gender=models.CharField(null=True,blank=True,max_length=8)
    facebook_url=models.CharField(null=True,blank=True,max_length=100)
    home_address=models.CharField(null=True,blank=True,max_length=50)
    major=models.CharField(null=True,blank=True,max_length=30)
    graduating_year=models.IntegerField(null=True,blank=True)
    recruitment_time=models.DateTimeField(auto_now_add=True,null=False,blank=False)
    ieee_id=models.IntegerField(null=True,blank=True)
    session_id=models.IntegerField(null=False,blank=True)
    payment_status=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="Recruited Members"
    
    def __str__(self) -> str:
        return str(self.nsu_id)
    def get_absolute_url(self):
        return reverse("recruited member", kwargs={"nsu_id": self.nsu_id})
    
    