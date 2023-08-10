from django import forms
from .models import HomepageBannerPictureWithText

class HomePageBannerWithTextForm(forms.ModelForm):
    class Meta:
        model=HomepageBannerPictureWithText
        fields=['banner_picture','first_layer_text','second_layer_text','second_layer_text_colored','third_layer_text']