from django import forms
from port.models import Teams
import os

class TeamForm(forms.ModelForm):
    class Meta:
        model=Teams
        fields=[
            'team_name','team_short_description','team_picture','is_active'
        ]
    
    def save(self, commit=True):
        # Get the existing instance from the database
        instance = super().save(commit=False)
        print("In save")
        # Delete the previous image if it exists
        if instance.pk and 'team_picture' in self.changed_data:
            previous_instance = Teams.objects.get(pk=instance.pk)
            previous_picture = previous_instance.team_picture
            # Delete the associated file from the file system
            if previous_picture:
                if os.path.isfile(previous_picture.path):
                    os.remove(previous_picture.path)

            # Update the instance with the new image
            previous_instance.team_picture = instance.team_picture
            previous_instance.save()

        if commit:
            instance.save()
        return instance
