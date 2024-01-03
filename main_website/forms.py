from django import forms
from .models import HomePageTopBanner,IEEE_Bangladesh_Section
from ckeditor.widgets import CKEditorWidget

class HomePageTopBanner(forms.ModelForm):
    class Meta:
        model=HomePageTopBanner
        fields=['banner_picture','first_layer_text','second_layer_text','second_layer_text_colored','third_layer_text']

class About_IEEE_Bangladesh_Section_Form(forms.ModelForm):

    #It is a static variable which keeps a count of the number of form objects created in the page
    textarea_id_counter = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Here the id for each form object is attached to a function that will generate a unique id for each form object
        #Without this there cannot be multiple CKEditor boxes in a page as it will by default have the same id and it will cause clashing
        self.fields['caption'].widget = CKEditorWidget(attrs={'id': About_IEEE_Bangladesh_Section_Form.get_textarea_next_id()})

    #This function generates a unique id
    def get_textarea_next_id():
        #Create a unique id string using the static counter variable
        id_string = 'txtarea_id_' + str(About_IEEE_Bangladesh_Section_Form.textarea_id_counter)
        #Increment the counter
        About_IEEE_Bangladesh_Section_Form.textarea_id_counter += 1
        return id_string
    
    class Meta:
        model = IEEE_Bangladesh_Section
        fields = ['about_ieee_bangladesh','member_and_volunteer_description','benefits_description','student_branches_description','affinity_groups_description','community_and_society_description']