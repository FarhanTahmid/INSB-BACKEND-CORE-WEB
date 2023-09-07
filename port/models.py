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
    team_name=models.CharField(max_length=40,null=False,blank=False)
    primary=models.IntegerField(null=False,blank=False,default=0)
    # team_of attribute means to which SC_AG or Branch The Team is registered to
    team_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.team_name   

class Roles_and_Position(models.Model):
    id=models.IntegerField(null=False,blank=False,default=0,primary_key=True)
    role=models.CharField(max_length=40,null=False,blank=False)
    role_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)
    is_eb_member = models.BooleanField(default=False)
    is_sc_ag_eb_member=models.BooleanField(default=False)
    is_officer=models.BooleanField(default=False)
    is_faculty=models.BooleanField(default=False)
    
    class Meta:
        verbose_name='Registered positions'
    def __str__(self) -> str:
        return self.role
    
    