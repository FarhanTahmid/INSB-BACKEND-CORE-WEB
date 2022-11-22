from django import forms
from django.forms import ModelForm
from . models import recruited_members

class StudentForm(forms.ModelForm):
    class Meta:
        model=recruited_members
        fields='__all__'
