from django.db import models
from django.urls import reverse

# Create your models here.

#if you want to create an admin, go to django admin, insert data in this model, then register in users as superuser

class adminUsers(models.Model):
    username=models.CharField(primary_key=True,null=False,blank=False,max_length=30,default='Undetermined')
    name=models.CharField(null=False,blank=False,max_length=60,default="Undetermined")
    email=models.EmailField(null=False,blank=False,max_length=50)
    class Meta:
        verbose_name="Admin User"
    def __str__(self) -> str:
        return self.name
    def get_absolute_url(self):
        return reverse("admin_users", kwargs={"userid": self.userid})
        
    