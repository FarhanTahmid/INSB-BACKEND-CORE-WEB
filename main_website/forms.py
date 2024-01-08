from django import forms
from .models import About_IEEE, HomePageTopBanner,IEEE_Bangladesh_Section
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
        self.fields['achievements_description'].widget = CKEditorWidget()
    
    class Meta:
        model = IEEE_Bangladesh_Section
        fields = ['about_ieee_bangladesh', 'ieee_bangladesh_logo', 'ieee_bd_link', 'member_and_volunteer_description', 'member_and_volunteer_picture', 'benefits_description','student_branches_description','affinity_groups_description','community_and_society_description', 'achievements_description', 'chair_name', 'chair_email', 'secretary_name', 'secretary_email', 'office_secretary_name', 'office_secretary_number']

class About_IEEE_Form(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['about_ieee'].widget = CKEditorWidget()
        self.fields['community_description'].widget = CKEditorWidget()
        self.fields['start_with_ieee_description'].widget = CKEditorWidget()
        self.fields['collaboration_description'].widget = CKEditorWidget()
        self.fields['publications_description'].widget = CKEditorWidget()
        self.fields['events_and_conferences_description'].widget = CKEditorWidget()
        self.fields['achievements_description'].widget = CKEditorWidget()
        self.fields['innovations_and_developments_description'].widget = CKEditorWidget()
        self.fields['students_and_member_activities_description'].widget = CKEditorWidget()
        self.fields['quality_description'].widget = CKEditorWidget()
    
    class Meta:
        model = About_IEEE
        fields = ['about_ieee', 'about_image', 'learn_more_link', 'mission_and_vision_link', 'community_description', 'community_image', 'start_with_ieee_description', 'collaboration_description', 'publications_description', 'events_and_conferences_description', 'achievements_description', 'innovations_and_developments_description', 'innovations_and_developments_image', 'students_and_member_activities_description', 'students_and_member_activities_image', 'quality_description', 'quality_image', 'join_now_link', 'asia_pacific_link', 'ieee_computer_organization_link', 'customer_service_number', 'presidents_names', 'founders_names']