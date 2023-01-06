from django.db import models
from django.urls import reverse
from port.models import Teams
from users.models import Members

# Create your models here.

#if you want to create an admin, go to django admin, insert data in this model, then register in users as superuser

class adminUsers(models.Model):
    username=models.CharField(primary_key=True,null=False,blank=False,max_length=30,default='Undetermined')
    name=models.CharField(null=False,blank=False,max_length=60,default="Undetermined")
    profile_picture=models.ImageField(null=False,blank=False,default='Admin/admin_profile_pictures/default_profile_picture.png',upload_to='Admin/admin_profile_pictures/')
    email=models.EmailField(null=False,blank=False,max_length=50)
    class Meta:
        verbose_name="Admin User"
    def __str__(self) -> str:
        return self.name
    def get_absolute_url(self):
        return reverse("admin_users", kwargs={"userid": self.userid})
        
class Access_Criterias(models.Model):
    team=models.ForeignKey(Teams,null=False,blank=False,on_delete=models.CASCADE,default=13)
    criteria_name=models.CharField(null=False,blank=False,max_length=30,default="all")

    class Meta:
        verbose_name="Data Access Criteria"
    def __str__(self) -> str:
        return str(self.criteria_name)
    
class Team_Data_Access(models.Model):
    team=models.ForeignKey(Teams,null=False,blank=False,on_delete=models.CASCADE,verbose_name="Team")
    ieee_id=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    criteria=models.ForeignKey(Access_Criterias,null=True,blank=True,on_delete=models.CASCADE,verbose_name="Accepted Permission Criteria")
    has_permission=models.BooleanField(null=False,blank=False,default=False,verbose_name="Permission Status")
    class Meta:
        verbose_name="Team Data Access"
    def __str__(self) -> str:
        return str(self.ieee_id)