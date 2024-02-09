from django.db import models
from django.urls import reverse
from port.models import *
from recruitment.models import recruitment_session
from membership_development_team.models import Renewal_Sessions
from django.contrib.auth.models import User
from django_resized import ResizedImageField
from port.models import Panels

# from membership_development_team.models import Renewal_Sessions
# Create your models here.

class Members(models.Model):
    
    '''This is the main registered members database for IEEE NSU SB'''
    
    ieee_id=models.BigIntegerField(primary_key=True,blank=False,null=False)
    name=models.CharField(null=False,blank=False,max_length=100)
    nsu_id=models.BigIntegerField(null=True, blank=True)
    email_ieee=models.EmailField(null=True,blank=True)
    email_personal=models.EmailField(null=True,blank=True)
    email_nsu=models.EmailField(null=True,blank=True)
    major=models.CharField(null=True,blank=True,max_length=50)
    contact_no=models.CharField(null=True,blank=True,max_length=16)
    home_address=models.CharField(null=True,blank=True,max_length=200)
    date_of_birth=models.DateField(null=True,blank=True)
    gender=models.CharField(null=True,blank=True,max_length=7)
    facebook_url=models.URLField(null=True,blank=True,max_length=500)
    linkedin_url=models.URLField(null=True,blank=True,max_length=500)
    user_profile_picture=models.ImageField(null=True,blank=True,upload_to='user_profile_pictures/')
    team=models.ForeignKey(Teams,null=True,blank=True,on_delete=models.CASCADE)
    position=models.ForeignKey(Roles_and_Position,default=13,on_delete=models.CASCADE) #Default=13 means the position of a general member, check roles and positions table
    session=models.ForeignKey(recruitment_session,null=True,blank=True,on_delete=models.CASCADE) #recruitment session
    last_renewal_session=models.ForeignKey(Renewal_Sessions,null=True,blank=True,on_delete=models.CASCADE) #last renewal session    
    is_active_member = models.BooleanField(null=False,blank=False,default=True)
    is_blocked = models.BooleanField(null=False,blank=False,default=False)
    class Meta:
        verbose_name='INSB Registered Members'
        ordering = ['position__rank']
    
    def __str__(self) -> str:
        return str(self.ieee_id)
    def get_absolute_url(self):
        return reverse('registered member',kwargs={'member_id':self.ieee_id})
    
    def get_image_url(self):
        return self.user_profile_picture


'''This table will be used to get the data of the EX Panel Members of IEEE NSU SB '''

class Alumni_Members(models.Model):
    name=models.CharField(null=False,blank=False,max_length=100)
    picture=ResizedImageField(null=True,blank=True,default='user_profile_pictures/default_profile_picture.png',upload_to='panel_profile_pictures/')
    linkedin_link=models.URLField(null=True,blank=True,max_length=100)
    facebook_link=models.URLField(null=True,blank=True,max_length=100)
    email=models.URLField(null=True,blank=True,max_length=50)
    contact_no=models.CharField(null=True,blank=True,max_length=50)
    ieee_collaboratec=models.URLField(null=True,blank=True,max_length=100)
    
    class Meta:
        verbose_name='Alumni Members'
    
    def __str__(self) -> str:
        return str(self.pk)




'''This will create a table for Executive Commitee Members. Members will be assigned by years, and their positions. people who are registered already in INSB Database 
will be extracted from "Members" table and those who are not in insb database will be extracted from "Ex Panel Members" Table.
'''
class Panel_Members(models.Model):
    tenure=models.ForeignKey(Panels,on_delete=models.CASCADE) #think this like panel_pk
    member=models.ForeignKey(Members,on_delete=models.CASCADE,null=True,blank=True)
    ex_member=models.ForeignKey(Alumni_Members,on_delete=models.CASCADE,null=True,blank=True)
    position=models.ForeignKey(Roles_and_Position,on_delete=models.CASCADE)
    team=models.ForeignKey(Teams,null=True,blank=True,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name="Panel Members (Whole Tenure)"
        ordering=['position__rank']
    def __str__(self) -> str:
        return str(self.member) 
    

class ResetPasswordTokenTable(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    token=models.CharField(max_length=100,null= False,blank=False)
    
    class Meta:
        verbose_name="User Reset Password Tokens"
    def __str__(self) -> str:
        return str(self.pk)
    
class UserSignupTokenTable(models.Model):
    user=models.ForeignKey(Members,on_delete=models.CASCADE)
    token=models.CharField(max_length=100,null=False,blank=False)
    
    class Meta:
        verbose_name="User Signup Token"
    
    def __str__(self) -> str:
        return str(self.pk)
    
'''This class is for the number of daily hits on the page'''
class User_IP_Address(models.Model):
    ip_address = models.GenericIPAddressField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Visitors on Main Website"
    def __str__(self):
        return self.ip_address

class VolunteerAwardRecievers(models.Model):
    '''Stores the recievers of the particular awards'''
    award=models.ForeignKey(VolunteerAwards,null=False,blank=False,on_delete=models.CASCADE)
    award_reciever=models.ForeignKey(Members ,null=False,blank=False,on_delete=models.CASCADE)
    contributions=models.CharField(null=True,blank=True,max_length=600)
    
    class Meta:
        verbose_name="Award Recievers"
    def __str__(self) -> str:
        return str(self.award_reciever)

    