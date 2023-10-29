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
from django.contrib.auth.models import User
from django_resized import ResizedImageField
import datetime
from django.contrib.postgres.fields import ArrayField
from port.models import Panels

# from membership_development_team.models import Renewal_Sessions
# Create your models here.

class Members(models.Model):
    
    '''This is the main registered members database for IEEE NSU SB'''
    
    ieee_id=models.IntegerField(primary_key=True,blank=False,null=False)
    name=models.CharField(null=False,blank=False,max_length=100)
    nsu_id=models.IntegerField(null=False, blank=False)
    email_ieee=models.EmailField(null=True,blank=True)
    email_personal=models.EmailField(null=True,blank=True)
    email_nsu=models.EmailField(null=True,blank=True)
    major=models.CharField(null=True,blank=True,max_length=50)
    contact_no=models.CharField(null=True,blank=True,max_length=16)
    home_address=models.CharField(null=True,blank=True,max_length=200)
    date_of_birth=models.DateField(null=True,blank=True)
    gender=models.CharField(null=True,blank=True,max_length=7)
    facebook_url=models.URLField(null=True,blank=True,max_length=200)
    linkedin_url=models.URLField(null=True,blank=True,max_length=200)
    user_profile_picture=ResizedImageField(null=False,blank=False,default='user_profile_pictures/default_profile_picture.png',upload_to='user_profile_pictures/')
    team=models.ForeignKey(Teams,null=True,blank=True,on_delete=models.CASCADE)
    position=models.ForeignKey(Roles_and_Position,default=13,on_delete=models.CASCADE) #Default=13 means the position of a general member, check roles and positions table
    session=models.ForeignKey(recruitment_session,null=True,blank=True,on_delete=models.CASCADE) #recruitment session
    last_renewal_session=models.ForeignKey(Renewal_Sessions,null=True,blank=True,on_delete=models.CASCADE) #last renewal session
    panel_session=models.ForeignKey(Panels,null=True,blank=True,on_delete=models.CASCADE) #panel session of the member to identify in which panel he had his positin
    
    class Meta:
        verbose_name='INSB Registered Members'
    
    def __str__(self) -> str:
        return str(self.ieee_id)
    def get_absolute_url(self):
        return reverse('registered member',kwargs={'member_id':self.iee_id})


'''This table will be used to get the data of the EX Panel Members of IEEE NSU SB '''

class Ex_panel_members(models.Model):
    name=models.CharField(null=False,blank=False,max_length=100)
    picture=models.ImageField(null=True,blank=True,default='user_profile_pictures/default_profile_picture.png',upload_to='panel_profile_pictures/')
    linkedin_link=models.URLField(null=True,blank=True,max_length=100)
    facebook_link=models.URLField(null=True,blank=True,max_length=100)
    mail=models.URLField(null=True,blank=True,max_length=50)
    ieee_collaboratec=models.URLField(null=True,blank=True,max_length=100)
    
    class Meta:
        verbose_name='Ex Panel Members'
    
    def __str__(self) -> str:
        return self.name




# '''This will create a table for Executive Commitee Members. Members will be assigned by years, and their positions. people who are registered already in INSB Database 
# will be extracted from "Members" table and those who are not in insb database will be extracted from "Ex Panel Members" Table.
# '''
# class Executive_commitee_members(models.Model):
#     year=models.ForeignKey(Executive_commitee,on_delete=models.CASCADE)
#     member=models.ForeignKey(Members,on_delete=models.CASCADE,null=True,blank=True)
#     ex_member=models.ForeignKey(Ex_panel_members,on_delete=models.CASCADE,null=True,blank=True)
#     position=models.ForeignKey(Roles_and_Position,on_delete=models.CASCADE)
    
#     class Meta:
#         verbose_name="Executive Commitee Members" 

class ResetPasswordTokenTable(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    token=models.CharField(max_length=100,null= False,blank=False)
    
    class Meta:
        verbose_name="User Reset Password Tokens"
    def __str__(self) -> str:
        return str(self.pk)
    
'''This class is for the number of daily hits on the page'''
class User(models.Model):
    ip_address = models.TextField(default=None)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Visitors on Main Website"
    def __str__(self):
        return self.ip_address

    