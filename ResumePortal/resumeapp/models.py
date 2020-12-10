# -*- coding: utf-8 -*-
#from import unicode_literals

from django.db import models

# Create your models here.
# Create your models here.
class Resume(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=12)
    email_address = models.CharField(max_length=50)
    education = models.CharField(max_length=50,null=True)
    technical_skillset = models.CharField(max_length=400,null=True)
    work_experience = models.CharField(max_length=20,null=True)
    employment_authorization = models.CharField(max_length=10,null=True)
    loginid = models.EmailField(unique=True,null=True)
    password = models.CharField(max_length=50)
    registration = models.CharField(max_length=3,default='No')

    def __str__(self):
        return self.first_name+" "+self.last_name+" "+self.phone_number+" "+self.email_address+" "+self.education+" "+self.technical_skillset+" "+self.work_experience+" "+self.employment_authorization

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