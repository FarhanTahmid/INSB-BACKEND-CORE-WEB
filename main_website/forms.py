from django import forms
from .models import HomePageTopBanner,IEEE_Bangladesh_Section
from ckeditor.widgets import CKEditorWidget

class HomePageTopBanner(forms.ModelForm):
    class Meta:
        model=HomePageTopBanner
        fields=['banner_picture','first_layer_text','third_layer_text']

class About_IEEE_Bangladesh_Section_Form(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['about_ieee_bangladesh'].widget = CKEditorWidget()
        self.fields['member_and_volunteer_description'].widget = CKEditorWidget()
        self.fields['benefits_description'].widget = CKEditorWidget()
        self.fields['student_branches_description'].widget = CKEditorWidget()
        self.fields['affinity_groups_description'].widget = CKEditorWidget()
        self.fields['community_and_society_description'].widget = CKEditorWidget()
    
    class Meta:
        model = IEEE_Bangladesh_Section
        fields = ['about_ieee_bangladesh','member_and_volunteer_description','benefits_description','student_branches_description','affinity_groups_description','community_and_society_description']