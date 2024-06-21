from django.db import models
from ckeditor.fields import RichTextField
from django_resized import ResizedImageField

# Create your models here.
class Chapters_Society_and_Affinity_Groups(models.Model):
    '''This model Includes Branch and all the Society'''
    group_name=models.CharField(null=False,blank=False,max_length=150)
    primary=models.IntegerField(null=False,blank=False,default=0)
    short_form=models.CharField(null=True,blank=True,max_length=20)
    primary_color_code=models.CharField(null=True,blank=True,max_length=20)
    secondary_color_code = models.CharField(null=True,blank=True,max_length=20)
    mission_vision_color_code = models.CharField(null=True,blank=True,max_length=20)
    text_color_code = models.CharField(null=True,blank=True,max_length=20)
    logo=models.ImageField(null=True,blank=True,upload_to='sc_ag_logos/')

    '''The next attributes are for the Sc_Ag main page'''
    short_form_2 = models.CharField(null=True,blank=True,max_length=10)
    page_title = models.TextField(null=True,blank=True,default="",verbose_name="Page Title")
    secondary_paragraph = models.TextField(null=True,blank=True,default="",verbose_name="Second Paragraph")
    about_description = models.TextField(null=True,blank=True,default="",verbose_name="About")
    background_image = ResizedImageField(null=True,blank=True,upload_to="main_website_files/societies_&_ag/background_image/",verbose_name="Background Image")
    mission_description = models.TextField(null=True,blank=True,default="",verbose_name="Mission")
    mission_picture = ResizedImageField(null=True,blank=True,upload_to="main_website_files/societies_&_ag/mission_picture/",verbose_name="Mission Image")
    vision_description = models.TextField(null=True,blank=True,default="",verbose_name="Vission")
    vision_picture = ResizedImageField(null=True,blank=True,upload_to="main_website_files/societies_&_ag/vision_picture/",verbose_name="Vision Image")
    what_is_this_description = models.TextField(null=True,blank=True,default="",verbose_name=f"What is it about ?")
    why_join_it = models.TextField(null=True,blank=True,default="",verbose_name=f"Why join it ?")
    what_activites_it_has = models.TextField(null=True,blank=True,default="",verbose_name="What activities we usually do ?")
    how_to_join = models.TextField(null=True,blank=True,default="",verbose_name=f"How to join it ?")
    email = models.EmailField(null=True,blank=True)
    facebook_link = models.URLField(blank=True,null=True)

    class Meta:
        verbose_name="Chapters-Societies-Affinity Group"
    def __str__(self) -> str:
        return str(self.group_name) 
class Teams(models.Model):
    '''
    The main theory of the model is:
        -team_primary is the driving variable of the model, it identifies the team and it must remain same in every database.
        -team_of means for which society or affinity group the team is created.

    '''
    team_name=models.CharField(max_length=40,null=False,blank=False)
    team_short_description=RichTextField(null=True,blank=True,max_length=500)
    primary=models.IntegerField(null=False,blank=False,default=0)
    team_picture=ResizedImageField(null=True,blank=True,upload_to="Teams/team_images/")
    # team_of attribute means to which SC_AG or Branch The Team is registered to
    team_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)
    is_active=models.BooleanField(null=True,blank=True,default=True)
    completed_task_points = models.FloatField(null=False,blank=False,default=0)
    
    class Meta:
        verbose_name="Registered Team"
        ordering=['-is_active','team_name']
    def __str__(self) -> str:
        return self.team_name   

class Roles_and_Position(models.Model):
    '''
    The main theory of this model is:
        -id is the main driver of this model as it defines the hierarchy also. id starting with lowest position means the highest role in hierarchy. It must remain
        same as documentation in every database.
        -role_of means for which society or affinity group the role is created.
        -all other boolean fields are created to identify the Roles more precisely.
    '''
    id=models.IntegerField(null=False,blank=False,default=0,primary_key=True)
    role=models.CharField(max_length=40,null=False,blank=False)
    role_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)
    rank = models.IntegerField(null=True,blank=True,default=5000)
    is_eb_member = models.BooleanField(default=False)
    is_sc_ag_eb_member=models.BooleanField(default=False)
    is_officer=models.BooleanField(default=False)
    is_co_ordinator=models.BooleanField(default=False)
    is_faculty=models.BooleanField(default=False)
    is_mentor=models.BooleanField(default=False)
    is_core_volunteer=models.BooleanField(default=False)
    is_volunteer=models.BooleanField(default=False)
    
    class Meta:
        verbose_name='Registered positions'
        ordering=['-rank']
    def __str__(self) -> str:
        return self.role

'''This will create a table with panel years and a boolean value named "current" to check if it is the current panel or not '''

class Panels(models.Model):
    '''
    The main theory of this panel model is-
        -there must be only one instance that can have the currrent=False value. The system wont work if there are multiple instances that have the current=False attributes.
        -year indicates the tenure of the panel
        -creation_time is initialized whenever the panel is created from the Panel Page.
        -panel_of means for which society or AG the panel is for
    '''
    year=models.CharField(max_length=40,null=False,blank=False)
    creation_time=models.DateTimeField(null=True,blank=True)
    current=models.BooleanField(null=False,blank=False,default=False)
    panel_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)
    panel_end_time=models.DateTimeField(null=True,blank=True)
    
    class Meta:
        verbose_name='IEEE NSU SB Panels'
    def __str__(self) -> str:
        return str(self.year)

class VolunteerAwards(models.Model):
    '''The main theory of this volunteer award is-
        -Every panel will have own awards. Awards will be distinguished by panels
        -Every SC-AG will have their own awards. Awards will be distinguished by sc ags as well.
    '''
    volunteer_award_name=models.CharField(null=False,blank=False,max_length=100,verbose_name="Name of Award")
    panel=models.ForeignKey(Panels,null=False,blank=False,on_delete=models.CASCADE)
    award_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE)
    rank_of_awards=models.IntegerField(null=False,blank=False,default=0)
    
    class Meta:
        verbose_name="Volunteer Award"
        ordering=["-rank_of_awards"]
        
    def __str__(self):
        return self.volunteer_award_name
    
class SkillSetTypes(models.Model):
    '''Stores skillset types'''
    skill_type=models.CharField(null=False,blank=False,max_length=200)

    class Meta:
        verbose_name="Skill set Types"
    def __str__(self) -> str:
        return str(self.pk)

    
    
    