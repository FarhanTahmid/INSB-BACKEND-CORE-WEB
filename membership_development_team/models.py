from django.db import models
from django.urls import reverse
from users.models import Members
# Create your models here.

#Table for renewal Sessions, primary key is id
class Renewal_Sessions(models.Model):
    session_name=models.CharField(null=False,blank=False,max_length=30)
    session_time=models.DateField(null=False,blank=False)
    
    class Meta:
        verbose_name="Renewal Session"
    def __str__(self) -> str:
        return str(self.session_name)
    def get_absolute_url(self):
        return reverse("renewal_session", kwargs={"session_name": self.session_name})
    
#Table for renewal requests for every session, primary key is id. This table is View Protected. Donot register this in admin
class Renewal_requests(models.Model):
    session_id=models.ForeignKey(Renewal_Sessions,null=False,blank=False,on_delete=models.CASCADE)
    ieee_id=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE)
    email_personal=models.EmailField(null=False,blank=False)
    ieee_account_password=models.CharField(null=False,blank=False,max_length=50)
    renewal_status=models.BooleanField(null=False,blank=False,default=False)
    view_status=models.BooleanField(null=False,blank=False,default=False)
    
    # Warning! Don't register This Table in Admin! Security Issue #
    def __str__(self) -> str:
        return str(self.ieee_id)