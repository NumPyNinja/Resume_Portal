# -*- coding: utf-8 -*-
#from import unicode_literals

from django.db import models
from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
''' --------------------------------------------'''
"""-----------------------------------------------"""
# Create your models here.
class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB - 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", 0)

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            print (content_type)
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('File type is not supported.'))
        except AttributeError:
            pass

        return data
# Create your models here.
class ResumeUpload(models.Model):
      filename = ContentTypeRestrictedFileField(upload_to='media/', content_types=['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],max_upload_size=5242880,blank=False, null=False)

class Resume(models.Model):
    pass

class Candidate(models.Model):
    first_name = models.CharField(max_length=50 , null=False)
    last_name = models.CharField(max_length=50 , null=False)
    loginid = models.EmailField(unique=True,null=False )
    password = models.CharField(max_length=100,null=False )
    #-----------------------Email--------------------------------
    email_active_field = models.BooleanField(default=False, null=False)
    # -----------------------Email--------------------------------
    def __str__(self):
        return self.first_name + " " + self.last_name


class Candidate_Details(models.Model):

    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=12 ,null=False)
    email_address = models.CharField(unique=True,max_length=50 , null=False)
    education = models.CharField(max_length=50,null=True)
    technical_skillset = models.CharField(max_length=400,null=True)
    work_experience = models.CharField(max_length=400,null=True)
    employment_authorization = models.CharField(max_length=10,null=True)

    registration = models.CharField(max_length=3,default='No')
    # -----------------------form validation--------------------------------
    link_to_Resume_on_disk = models.FileField()

    def __str__(self):
        return self.phone_number+" "+self.email_address+" "+self.education+" "+self.technical_skillset+" "+self.work_experience+" "+self.employment_authorization

class Jobs(models.Model):
    job_title = models.CharField(max_length=50,null=True,blank=True)
    job_location = models.CharField(max_length=50,null=True)

    def __str__(self):
        return  str(self.job_title) + " " + str(self.job_location)

class Job_Details(models.Model):
    job_category = models.CharField(max_length=50, null=True)
    date_time_scrapped = models.CharField(max_length=50,null=True)
    searched_job_title = models.CharField(max_length=100, null=True)
    searched_job_location = models.CharField(max_length=100, null=True)
    job_portal = models.CharField(max_length=50, null=True)
    job_date_posted=  models.CharField(max_length=100,null=True)
    job_title = models.CharField(max_length=400, null=True)
    job_company_name = models.CharField(max_length=400, null=True)
    job_location = models.CharField(max_length=400, null=True)
    job_phone_no = models.CharField(max_length=100, null=True)
    job_email = models.CharField(max_length=200, null=True)
    job_link = models.CharField(max_length=2000, null=True)
    job_description = models.TextField(null=True)

    def __str__(self):
        return self.job_category+self.date_time_scrapped+self.searched_job_title+self.searched_job_location+self.job_portal+self.job_title+self.company_name+self.job_location+self.job_phone_no+self.job_email+self.job_link+self.job_description