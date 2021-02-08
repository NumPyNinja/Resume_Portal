from django import forms
from django.db import models
from .models import ResumeUpload




class UploadForm(forms.ModelForm): 
    class Meta:
         model = ResumeUpload
         fields = ('filename', )

