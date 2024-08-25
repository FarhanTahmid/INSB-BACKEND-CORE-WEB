from django import forms
from . models import *

class EventForm(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['event_description']

class EventFormGC(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['event_description_for_gc']
        labels = {
            'event_description_for_gc': 'Event Description For Google Calendar',
        }