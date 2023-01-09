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
        

    
class MDT_Data_Access(models.Model):
    
    ieee_id=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    renewal_data_access=models.BooleanField(null=False,blank=False,default=False,verbose_name='Membership Renewal Data Access Permission')
    insb_member_details=models.BooleanField(null=False,blank=False,default=False,verbose_name="INSB Registered Member Details Permission")
    recruitment_session=models.BooleanField(null=False,blank=False,default=False,verbose_name="Recruitment Data View Permission")
    recruited_member_details=models.BooleanField(null=False,blank=False,default=False,verbose_name="Rectuited Member Details Permission")
    
    class Meta:
        verbose_name="Membership Development Team Data Access"
    def __str__(self) -> str:
        return str(self.ieee_id)