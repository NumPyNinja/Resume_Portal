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