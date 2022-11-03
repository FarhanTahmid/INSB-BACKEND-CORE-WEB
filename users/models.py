from email.policy import default
from pyexpat import model
from tabnanny import verbose
from tokenize import blank_re
from unittest.util import _MAX_LENGTH
from django.db import models
from django.urls import reverse

# Create your models here.
class Members(models.Model):

    iee_id=models.IntegerField(primary_key=True,blank=False,null=False)
    name=models.CharField(null=False,blank=False,max_length=100)
    nsu_id=models.IntegerField(null=False, blank=False)
    email_ieee=models.EmailField(null=False,blank=False)
    email_personal=models.EmailField(null=False,blank=False)
    contact_no=models.CharField(null=True,blank=True,max_length=16)
    home_address=models.CharField(null=True,blank=True,max_length=200)
    date_of_birth=models.DateField(null=True,blank=True)
    gender=models.CharField(null=False,blank=True,max_length=7)
    facebook_url=models.URLField(null=True,blank=True,max_length=200)
    
    class Meta:
        verbose_name='INSB Registered Members'
    
    def __str__(self) -> str:
        return self.name
    def get_absolute_url(self):
        return reverse('registered member',kwargs={'member_id':self.iee_id})

    