from django import forms
import os
from main_website.models import *

class AchievementForm(forms.ModelForm):
    class Meta:
        model=Achievements
        fields=[
            'award_name','award_winning_year','award_description','award_picture','award_of'
        ]
    
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)

        # Delete the previous image if it exists
        if instance.pk and 'award_picture' in self.changed_data:
            previous_instance = Achievements.objects.get(pk=instance.pk)
            previous_picture = previous_instance.award_picture

            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)

            # Update the instance with the new image
            previous_instance.award_picture = instance.award_picture
            previous_instance.save()

        if commit:
            instance.save()
        return instance

class NewsForm(forms.ModelForm):
    class Meta:
        model=News
        fields=[
            'news_title', 'news_subtitle', 'news_description','news_picture','news_date'
        ]
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)

        # Delete the previous image if it exists
        if instance.pk and 'news_picture' in self.changed_data:
            previous_instance = News.objects.get(pk=instance.pk)
            previous_picture = previous_instance.news_picture

            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)

            # Update the instance with the new image
            previous_instance.news_picture = instance.news_picture
            previous_instance.save()

        if commit:
            instance.save()
        return instance