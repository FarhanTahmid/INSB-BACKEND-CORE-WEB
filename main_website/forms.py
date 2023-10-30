from django import forms
from .models import HomePageTopBanner

class HomePageTopBanner(forms.ModelForm):
    class Meta:
        model=HomePageTopBanner
        fields=['banner_picture','first_layer_text','second_layer_text','second_layer_text_colored','third_layer_text']