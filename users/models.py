from email.policy import default
from pyexpat import model
from tabnanny import verbose
from tokenize import blank_re
from unittest.util import _MAX_LENGTH
from django.db import models
from django.urls import reverse
from insb_port import settings
from port.models import Teams,Roles_and_Position
from recruitment.models import recruitment_session
from membership_development_team.models import Renewal_Sessions
# from membership_development_team.models import Renewal_Sessions
# Create your models here.

class Members(models.Model):
    
    '''This is the main registered members database for IEEE NSU SB'''
    
    ieee_id=models.IntegerField(primary_key=True,blank=False,null=False)
    name=models.CharField(null=False,blank=False,max_length=100)
    nsu_id=models.IntegerField(null=False, blank=False)
    email_ieee=models.EmailField(null=True,blank=True)
    email_personal=models.EmailField(null=False,blank=False)
    major=models.CharField(null=True,blank=True,max_length=50)
    contact_no=models.CharField(null=True,blank=True,max_length=16)
    home_address=models.CharField(null=True,blank=True,max_length=200)
    date_of_birth=models.DateField(null=True,blank=True)
    gender=models.CharField(null=True,blank=True,max_length=7)
    facebook_url=models.URLField(null=True,blank=True,max_length=200)
    linkedin_url=models.URLField(null=True,blank=True,max_length=200)
    user_profile_picture=models.ImageField(null=False,blank=False,default='user_profile_pictures/default_profile_picture.png',upload_to='user_profile_pictures/')
    team=models.ForeignKey(Teams,null=True,blank=True,on_delete=models.CASCADE)
    position=models.ForeignKey(Roles_and_Position,default=13,on_delete=models.CASCADE) #Default=13 means the position of a general member, check roles and positions table
    session=models.ForeignKey(recruitment_session,null=True,blank=True,on_delete=models.CASCADE) #recruitment session
    last_renewal_time=models.DateField(blank=True,null=True,auto_now_add=False) #registers the last renewal
    last_renewal_session=models.CharField(blank=True,null=True,max_length=50) #registers the last renewal session
    last_renewal_session2=models.ForeignKey(Renewal_Sessions,null=True,blank=True,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name='INSB Registered Members'
    
    def __str__(self) -> str:
        return str(self.ieee_id)
    def get_absolute_url(self):
        return reverse('registered member',kwargs={'member_id':self.iee_id})


    