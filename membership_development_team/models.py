from django.db import models
from django.urls import reverse
from django_resized import ResizedImageField
from port.models import Teams, Roles_and_Position

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
    timestamp=models.DateTimeField(null=True,blank=True)
    session_id=models.ForeignKey(Renewal_Sessions,null=False,blank=False,on_delete=models.CASCADE)
    ieee_id=models.BigIntegerField(null=False,blank=False,default=0)
    nsu_id=models.BigIntegerField(null=False,blank=False,default=0)
    name=models.CharField(null=False,blank=False,max_length=100,default="null")
    contact_no=models.CharField(null=False,blank=False,max_length=30,default="null")
    email_associated=models.EmailField(null=False,blank=False)
    email_ieee=models.EmailField(null=True,blank=True)
    ieee_account_password=models.CharField(null=False,blank=False,max_length=500)
    
    #this *_check fields refers to the subscriptions the user is selecting on the forms.
    ieee_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    pes_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    ras_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    ias_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    wie_renewal_check=models.BooleanField(null=False,blank=False,default=False)
    
    transaction_id=models.CharField(null=True,blank=True,max_length=80)
    # The comment will be from applicant
    comment=models.CharField(null=True,blank=True,max_length=100) #the comment left by the applicant while applying
    
    renewal_status=models.BooleanField(null=False,blank=False,default=False)
    view_status=models.BooleanField(null=False,blank=False,default=False)
    
    official_comment=models.CharField(null=True,blank=True,max_length=150) #the comment that team member leaves while renewal time
    
    # Warning! Don't register This Table in Admin! Security Issue #
    class Meta:
        verbose_name="Renewal Requests"
    def __str__(self) -> str:
        return self.name


#Table For renewal Form information datas
class Renewal_Form_Info(models.Model):
    #primary key of each form will be the primary key of renewal session
    form_id=models.IntegerField(primary_key=True,null=False,blank=False,default=0)
    #to identify the form with session name we are using this session
    session=models.ForeignKey(Renewal_Sessions,on_delete=models.CASCADE,null=True,blank=True)
    #details of the form
    form_description=models.TextField(null=True,blank=True,max_length=1000)
    #membership payment amount details
    ieee_membership_amount=models.CharField(null=True,blank=True,max_length=50)
    ieee_ras_membership_amount=models.CharField(null=True,blank=True,max_length=50)
    ieee_pes_membership_amount=models.CharField(null=True,blank=True,max_length=50)
    ieee_ias_membership_amount=models.CharField(null=True,blank=True,max_length=50)
    ieee_wie_membership_amount=models.CharField(null=True,blank=True,max_length=50)
    #payment method details
    bkash_payment_number=models.CharField(null=True,blank=True,max_length=20)
    nagad_payment_number=models.CharField(null=True,blank=True,max_length=20)
    #further contact member id
    further_contact_member_id=models.CharField(null=True,blank=True,max_length=50)
    # form accepting response
    accepting_response=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="Renewal Form Detail"
    def __str__(self) -> str:
        return str(self.pk)
        


#TABLE FOR WEBSITE JOINING REQUEST

class Portal_Joining_Requests(models.Model):
    ieee_id=models.BigIntegerField(primary_key=True,blank=False,null=False)
    name=models.CharField(null=False,blank=False,max_length=100)
    nsu_id=models.BigIntegerField(null=True, blank=True)
    email_ieee=models.EmailField(null=True,blank=True)
    email_nsu=models.EmailField(null=True,blank=True)
    email_personal=models.EmailField(null=False,blank=False)
    major=models.CharField(null=True,blank=True,max_length=50)
    contact_no=models.CharField(null=True,blank=True,max_length=16)
    home_address=models.CharField(null=True,blank=True,max_length=200)
    date_of_birth=models.DateField(null=True,blank=True)
    gender=models.CharField(null=True,blank=True,max_length=7)
    facebook_url=models.URLField(null=True,blank=True,max_length=500)
    linkedin_url=models.URLField(null=True,blank=True,max_length=500)
    team=models.ForeignKey(Teams,null=True,blank=True,on_delete=models.CASCADE)
    position=models.ForeignKey(Roles_and_Position,default=13,on_delete=models.CASCADE) #Default=13 means the position of a general member, check roles and positions table
    application_status=models.BooleanField(null=False,blank=False,default=False)
    view_status=models.BooleanField(null=False,blank=False,default=False)
    user_profile_picture=ResizedImageField(null=True,blank=True,upload_to='user_profile_pictures/')
    
    class Meta:
        verbose_name='Portal Joining Requests'
    
    def __str__(self) -> str:
        return str(self.ieee_id)
    def get_absolute_url(self):
        return reverse('joining_requests',kwargs={'member_id':self.iee_id})
