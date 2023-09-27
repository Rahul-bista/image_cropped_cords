from django import forms

from .models import ImageLabel


class LabelForm(forms.ModelForm):
    class Meta:
        model = ImageLabel
        fields = ('original_image', 'mask_image')
