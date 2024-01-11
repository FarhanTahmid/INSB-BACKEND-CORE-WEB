from django import forms
from port.models import Chapters_Society_and_Affinity_Groups, Teams
from ckeditor.widgets import CKEditorWidget
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

class Chapter_Society_Affinity_Groups_Form(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['about_description'].widget = CKEditorWidget()
        self.fields['mission_description'].widget = CKEditorWidget()
        self.fields['vision_description'].widget = CKEditorWidget()
        self.fields['what_is_this_description'].widget = CKEditorWidget()
        self.fields['why_join_it'].widget = CKEditorWidget()
        self.fields['what_activites_it_has'].widget = CKEditorWidget()
        self.fields['how_to_join'].widget = CKEditorWidget()
    
    class Meta:
        model=Chapters_Society_and_Affinity_Groups
        fields=[
            'group_name','primary','short_form','primary_color_code','secondary_color_code','mission_vision_color_code','text_color_code','logo','short_form_2','page_title','secondary_paragraph','about_description','sc_ag_logo','background_image','mission_description','mission_picture','vision_description','vision_picture','what_is_this_description',
            'why_join_it','what_activites_it_has','how_to_join','email','facebook_link'
        ]
