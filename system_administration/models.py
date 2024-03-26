from django.db import models
from django.urls import reverse
from port.models import Teams
from users.models import Members
from django_resized import ResizedImageField
from ckeditor.fields import RichTextField
from port.models import Chapters_Society_and_Affinity_Groups
from chapters_and_affinity_group.models import SC_AG_Members
import os
from insb_port import settings
from PIL import Image
# Create your models here.

# System Model
class system(models.Model):
    system_under_maintenance=models.BooleanField(null=False,blank=False,default=False)
    main_website_under_maintenance=models.BooleanField(null=False,blank=False,default=False)
    portal_under_maintenance=models.BooleanField(null=False,blank=False,default=False)
    scheduling_under_maintenance = models.BooleanField(null=False,blank=False,default=False)
    restrict_sc_ag_updates = models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="System Handling"
    
    def __str__(self) -> str:
        return str(self.pk)


#if you want to create an admin, go to django admin, insert data in this model, then register in users as superuser
class adminUsers(models.Model):
    username=models.CharField(primary_key=True,null=False,blank=False,max_length=30,default='Undetermined')
    name=models.CharField(null=False,blank=False,max_length=60,default="Undetermined")
    profile_picture=models.ImageField(null=False,blank=False,default='Admin/admin_profile_pictures/default_profile_picture.png',upload_to='Admin/admin_profile_pictures/')
    email=models.EmailField(null=False,blank=False,max_length=50)

    def save(self, *args, **kwargs):

        if self.pk:
            try:
                # Retrieve the original instance from the database
                original_instance = adminUsers.objects.get(pk=self.pk)
                # Check if the profile picture field has changed 
                if original_instance.profile_picture != self.profile_picture:
                    # Remove the existing profile picture from the data base
                    if original_instance.profile_picture and os.path.isfile(original_instance.profile_picture.path):
                        os.remove(original_instance.profile_picture.path)
                    # Resize and compress the new image
                    _, ext = os.path.splitext(self.profile_picture.name)
                    profile_picture_path = os.path.join('Admin', 'admin_profile_pictures', f"{self.pk}_profile_picture{ext}")
                    compressed_profile_picture_path = os.path.join(settings.MEDIA_ROOT, profile_picture_path)
                    if self.profile_picture:
                        image = Image.open(self.profile_picture)
                        image.thumbnail((800, 800), Image.ANTIALIAS)  

                        if image.format == 'png':
                            
                            with Image.open(self.profile_picture) as img:
                                # Convert the image to RGB mode (if it's in RGBA mode)
                                if img.mode in ('RGBA', 'LA'):
                                    img = img.convert('RGB')
                                
                                # Save the image with the specified quality
                                img.save(compressed_profile_picture_path, format='PNG', quality=85, optimize=True)
                        else:
                            image.save(compressed_profile_picture_path, quality=85, optimize=True)
                            self.profile_picture = profile_picture_path

                elif not original_instance.profile_picture and self.profile_picture:
                    # If there was no profile picture initially, compress the new image
                    image = Image.open(self.profile_picture)
                    image.thumbnail((800, 800), Image.ANTIALIAS)
                    if image.format == 'png':
                        
                        with Image.open(self.profile_picture) as img:
                            # Convert the image to RGB mode (if it's in RGBA mode)
                            if img.mode in ('RGBA', 'LA'):
                                img = img.convert('RGB')
                            img.save(compressed_profile_picture_path, format='PNG', quality=85, optimize=True)
                    else:
                        image.save(compressed_profile_picture_path, quality=85, optimize=True)
                        self.profile_picture = profile_picture_path
            
            except adminUsers.DoesNotExist:
                pass
                         
        super().save(*args, **kwargs)

    class Meta:
        verbose_name="Admin User"
    def __str__(self) -> str:
        return self.name
    def get_absolute_url(self):
        return reverse("admin_users", kwargs={"userid": self.userid})
        
class Branch_Data_Access(models.Model):
    ieee_id=models.OneToOneField(Members,null=False,blank=False,on_delete=models.CASCADE)
    create_event_access=models.BooleanField(null=False,blank=False,default=False)
    event_details_page_access=models.BooleanField(null=False,blank=False,default=False)
    create_individual_task_access=models.BooleanField(null=False,blank=False,default=False)
    create_team_task_access=models.BooleanField(null=False,blank=False,default=False)
    create_panels_access=models.BooleanField(null=False,blank=False,default=False)
    panel_memeber_add_remove_access=models.BooleanField(null=False,blank=False,default=False)
    team_details_page=models.BooleanField(null=False,blank=False,default=False)
    manage_award_access=models.BooleanField(null=False,blank=False,default=False)
    manage_web_access=models.BooleanField(null=False,blank=False,default=False)

    class Meta:
        verbose_name="Branch Data Access"
    def __str__(self) -> str:
        return str(self.pk)
    
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


# Class for Public Relation Team data access
class LAO_Data_Access(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Access")

    class Meta:

        verbose_name = "Manage Team Access - Logistics and Operations Team"

    def __str__(self):
        return str(self.ieee_id)
    
# Class for Content Writing and Publications Team data access
class CWP_Data_Access(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Access")
    event_access = models.BooleanField(default=False,null=False,blank=False, verbose_name="Event Access")
    content_access = models.BooleanField(default=False,null=False,blank=False, verbose_name="Content Access")
    content_view_access = models.BooleanField(default=False,null=False,blank=False, verbose_name="Content View Access")

    class Meta:

        verbose_name = "Manage Team Access - Content Writing and Publications Team"

    def __str__(self):
        return str(self.ieee_id)
    
# Class for Promotions Team data access
class Promotions_Data_Access(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Access")

    class Meta:

        verbose_name = "Manage Team Access - Promotions Team"

    def __str__(self):
        return str(self.ieee_id)
    
# Class for Website Development Team data access
class WDT_Data_Access(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Access")

    class Meta:

        verbose_name = "Manage Team Access - Website Development Team"

    def __str__(self):
        return str(self.ieee_id)
    
# Class for Media Team data access
class Media_Data_Access(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Access")
    event_access = models.BooleanField(default=False,null=False,blank=False, verbose_name="Event Access")
    
    class Meta:

        verbose_name = "Manage Team Access - Media Team"

    def __str__(self):
        return str(self.ieee_id)
    
# Class for Graphics Team data access
class Graphics_Data_Access(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Manage Team Access")
    event_access = models.BooleanField(default=False,null=False,blank=False, verbose_name="Event Access")
    graphics_access = models.BooleanField(default=False,null=False,blank=False, verbose_name="Graphics Access")
    graphics_view_access = models.BooleanField(default=False,null=False,blank=False, verbose_name="Graphics View Access")

    class Meta:

        verbose_name = "Manage Team Access - Graphics Team"

    def __str__(self):
        return str(self.ieee_id)
    
# Class for Finance and Corporate Team data access
class FCT_Data_Access(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Access")

    class Meta:

        verbose_name = "Manage Team Access - Finance and Corporate Team"

    def __str__(self):
        return str(self.ieee_id)
    
#class for Events and Management Team data access
class EMT_Data_Access(models.Model):

    ieee_id=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    assign_task_data_access = models.BooleanField(null=False,blank=False,default=False,verbose_name="Task Assign Data Access Permission")
    manage_team_data_access = models.BooleanField(null=False,blank=False,default=False,verbose_name="Manage Team Permission")

    class Meta:
        verbose_name="Events and Management Team Data Access"
    def __str__(self):
        return str(self.ieee_id)

# class for SC AG Data Access
class SC_AG_Data_Access(models.Model):
    member=models.ForeignKey(SC_AG_Members,on_delete=models.CASCADE,null=False,blank=False)
    data_access_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,on_delete=models.CASCADE,null=False,blank=False,default=1)
    member_details_access=models.BooleanField(null=False,blank=False,default=False)
    create_event_access=models.BooleanField(null=False,blank=False,default=False)
    event_details_edit_access=models.BooleanField(null=False,blank=False,default=False)
    panel_edit_access=models.BooleanField(null=False,blank=False,default=False)
    membership_renewal_access=models.BooleanField(null=False,blank=False,default=False)
    manage_web_access=models.BooleanField(null=False,blank=False,default=False)
    manage_access=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="Manage Data Access - Chapter, Society, Affinity Group"
    
    def __str__(self) -> str:
        return str(self.member)

#these are for developers database
class Developer_criteria(models.Model):
    '''This class defines the developer types'''
    developer_type=models.CharField(null=False,blank=False,max_length=50)
    class Meta:
        verbose_name="Developer Criteria"
    def __str__(self)->str:
        return str(self.developer_type)
        
class Project_leads(models.Model):
    name=models.CharField(null=False,blank=False,max_length=50)
    developer_type=models.ForeignKey(Developer_criteria,null=True,blank=True,on_delete=models.CASCADE)
    developer_decription=models.CharField(null=True,blank=True,max_length=200)
    developers_picture=models.ImageField(null=True,blank=True,default='user_profile_pictures/default_profile_picture.png',upload_to='Admin/developers_pictures')
    facebook_url=models.URLField(null=True,blank=True,max_length=200)
    linkedin_url=models.URLField(null=True,blank=True,max_length=200)
    github_url=models.URLField(null=True,blank=True,max_length=200)
    
    class Meta:
        verbose_name="Project Lead"
    def __str__(self)->str:
        return str(self.name)

class Project_Developers(models.Model):
    name=models.CharField(null=False,blank=False,max_length=50)
    developer_type=models.ForeignKey(Developer_criteria,null=True,blank=True,on_delete=models.CASCADE)
    developer_decription=models.CharField(null=True,blank=True,max_length=200)
    developers_picture=models.ImageField(null=True,blank=True,default='user_profile_pictures/default_profile_picture.png',upload_to='Admin/developers_pictures')
    facebook_url=models.URLField(null=True,blank=True,max_length=200)
    linkedin_url=models.URLField(null=True,blank=True,max_length=200)
    github_url=models.URLField(null=True,blank=True,max_length=200)
    reputation_point=models.IntegerField(null=False,blank=False,default=0)
    
    class Meta:
        verbose_name="Project Developers"
    def __str__(self)->str:
        return str(self.name)


class SystemErrors(models.Model):
    date_time=models.DateTimeField(null=False,blank=False)
    error_name=models.CharField(null=False,blank=False,max_length=500)
    error_traceback=RichTextField(null=False,blank=False,max_length=3000)
    error_fix_status=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="System Error"
    def __str__(self) -> str:
        return str(self.pk)
