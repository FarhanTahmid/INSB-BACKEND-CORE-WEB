from django import forms
from  .models import *
from ckeditor.widgets import CKEditorWidget

class Content_Form(forms.ModelForm):
    textarea_id_counter = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].widget = CKEditorWidget(attrs={'id': Content_Form.get_textarea_next_id()})

    def get_textarea_next_id():
        id_string = 'txtarea_id_' + str(Content_Form.textarea_id_counter)
        Content_Form.textarea_id_counter += 1
        return id_string
    
    class Meta:
        model = Content_Notes
        fields = ['notes']