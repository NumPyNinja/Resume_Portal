from django import forms
from django.db import models
from .models import Resume


class UploadForm(forms.ModelForm): 
    class Meta:
         model = Resume
         fields = ('link_to_Resume_on_disk', )

