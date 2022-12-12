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
    #ieee_id=models.ForeignKey(Members,null=True,blank=True,on_delete=models.CASCADE)
    name=models.CharField(null=False,blank=False,max_length=100,default="null")
    contact_no=models.CharField(null=False,blank=False,max_length=30,default="null")
    email_personal=models.EmailField(null=False,blank=False)
    ieee_account_password=models.CharField(null=False,blank=False,max_length=50)
    
    #this *_check fields refers to the subscriptions the user is selecting on the forms.
    ieee_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    pes_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    ras_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    ias_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    wie_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    
    transaction_id=models.CharField(null=True,blank=True,max_length=80)
    comment=models.CharField(null=True,blank=True,max_length=100) #the comment left by the applicant while applying
    
    renewal_status=models.BooleanField(null=False,blank=False,default=False)
    view_status=models.BooleanField(null=False,blank=False,default=False)
    
    official_comment=models.CharField(null=True,blank=True,max_length=150) #the comment that team member leaves while renewal time
    
    # Warning! Don't register This Table in Admin! Security Issue #
    class Meta:
        verbose_name="Renewal Requests"
    def __str__(self) -> str:
        return self.name