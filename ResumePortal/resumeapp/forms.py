from django import forms
from django.db import models
from .models import ResumeUpload,Candidate,Candidate_Details

c_employment_authorization = [
    ('H1 B', 'H1 B'), ('H4', 'H4'), ('H4 EAD', 'H4 EAD'),
    ('B1', 'B1'), ('L1', 'L1'), ('L2', 'L2'), ('F1', 'F1')]


class UploadForm(forms.ModelForm): 
    class Meta:
         model = ResumeUpload
         fields = ('filename', )

class UserLoginForm(forms.ModelForm):
    loginid = forms.EmailField(
        error_messages={'invalid': 'Email error msg.'},
        widget=forms.TextInput(attrs={'class': 'input-text'}),
        required=True)
    password = forms.CharField(widget= forms.PasswordInput( attrs={'class': 'input-text'} ))

    class Meta:
        model = Candidate
        fields = ( 'loginid',  'password' )

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ('first_name', 'last_name' )

class Candidate_DetailsForm(forms.ModelForm):
    employment_authorization = forms.ChoiceField(widget=forms.Select(), choices=c_employment_authorization)
    email_address = forms.EmailField(
        error_messages={'invalid': 'Email error msg.'},
        widget=forms.TextInput(attrs={'class': 'search-field'}),
        required=True)
    class Meta:
        model = Candidate_Details
        fields = ( 'phone_number', 'email_address','education','technical_skillset',
                   'work_experience','employment_authorization')
