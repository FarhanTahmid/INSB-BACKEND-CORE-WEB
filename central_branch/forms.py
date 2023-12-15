from django import forms
from main_website.models import *

class AchievementForm(forms.ModelForm):
    class Meta:
        model=Achievements
        fields=[
            'award_name','award_winning_year','award_description','award_picture'
        ]