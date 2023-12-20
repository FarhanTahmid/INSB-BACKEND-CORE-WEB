from django import forms
from  .models import *

class Content_Form(forms.ModelForm):
    class Meta:
        model = Content_Notes
        fields = ['notes']