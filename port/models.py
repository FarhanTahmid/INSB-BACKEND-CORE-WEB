from django.db import models
# Create your models here.
class Chapters_Society_and_Affinity_Groups(models.Model):
    '''This model Includes Branch and all the Society'''
    group_name=models.CharField(null=False,blank=False,max_length=150)
    primary=models.IntegerField(null=False,blank=False,default=0)

    class Meta:
        verbose_name="Chapters-Societies-Affinity Group"
    def __str__(self) -> str:
        return self.group_name 

class Teams(models.Model):
    '''
    The main theory of the model is:
        -team_primary is the driving variable of the model, it identifies the team and it must remain same in every database.
        -team_of means for which society or affinity group the team is created.

    '''
    team_name=models.CharField(max_length=40,null=False,blank=False)
    primary=models.IntegerField(null=False,blank=False,default=0)
    # team_of attribute means to which SC_AG or Branch The Team is registered to
    team_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)
    
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
    is_eb_member = models.BooleanField(default=False)
    is_sc_ag_eb_member=models.BooleanField(default=False)
    is_officer=models.BooleanField(default=False)
    is_co_ordinator=models.BooleanField(default=False)
    is_faculty=models.BooleanField(default=False)
    
    class Meta:
        verbose_name='Registered positions'
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
    
    class Meta:
        verbose_name='IEEE NSU SB Panels'
    def __str__(self) -> str:
        return str(self.year)
    
    