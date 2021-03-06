# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.template import RequestContext
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from pyresparser import ResumeParser
from passlib.hash import sha256_crypt
import glob
import pandas
from . import models
import docx
import os
from docx import Document
import json
from .models import Candidate, Candidate_Details , Job_Details
from .forms import UploadForm,CandidateForm,Candidate_DetailsForm,UserLoginForm

import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib import messages
import boto3
import botocore
from datetime import datetime
from collections import defaultdict

#-----------------------Email--------------------------------

from django.core.mail import send_mail, EmailMessage
from django.utils.encoding import force_bytes
import six  # email
from passlib.hash import sha256_crypt
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

#-----------------------Email--------------------------------
# Open upload page
def upload_page(request):
    request.session.set_test_cookie()

    if request.session.has_key('eid'):
        return render(request, 'resumeapp/Job_Search_Results.html', {'udata': request.session['eid']})
    else:
        U_form = UploadForm()
        totaljobs = Job_Details.objects.all().count()
        return render(request, 'resumeapp/Homepage.html', {'totaljobs': totaljobs , 'form': U_form })

#Open  the my account page
def my_account(request):
    userLoginForm = UserLoginForm()
    return render(request, 'resumeapp/my_account.html' , {'form': userLoginForm  } )

#Open job search page
def job_search(request):

    return render(request, 'resumeapp/Job_Search.html')


#Open  the applicant details page
def applicant_file(request):

    if request.method == 'POST':

        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():

            fileuploaded = request.FILES['filename']
            fs = FileSystemStorage()
            fs.save(fileuploaded.name, fileuploaded)

            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            dir_location = os.path.join(BASE_DIR, 'media')
            file_location = dir_location + "/*.docx"

            list_of_files = glob.glob(file_location)
            latest_file = max(list_of_files, key=os.path.getctime)

        # Parse the uploaded resume
            parsed_details = ResumeParser(latest_file).get_extracted_data()
            resume_dict =  parsed_details

            candidateForm = CandidateForm()
            # ContactForm(initial={'subject': 'Hi there!'})
            candidateForm = CandidateForm(
                                       initial={ 'first_name': resume_dict.get("name"),
                                                 'last_name': resume_dict.get("name")
                                                }
                                 )

            candidate_DetailsForm = Candidate_DetailsForm()
            print (resume_dict)
            candidate_DetailsForm  = Candidate_DetailsForm( initial={
                                                    'phone_number': resume_dict.get("mobile_number"),
                                                    'email_address': resume_dict.get("email"),
                                                    'work_experience': resume_dict.get("experience"),
                                                    'technical_skillset': resume_dict.get("skills"),
                                                    'education': resume_dict.get("degree")
                                                      }
                                                    )
            # print(candidate_DetailsForm)
            # resume.save() // jira 81 error
            context = {'candidate': candidateForm , 'candidate_Details': candidate_DetailsForm }

            return render(request, 'resumeapp/Applicants_Detail.html', context)
        else:
            print("form is not valid")
            form = UploadForm(request.POST, request.FILES)
            totaljobs = Job_Details.objects.all().count()
            return render(request, 'resumeapp/Homepage.html', {'totaljobs': totaljobs , 'form': form })


#Getparsed Details from second page and store in DB
def update_db(request):
    if request.method == 'POST':
          Fcandidate_Details = Candidate_DetailsForm(request.POST)
          Fcandidate = CandidateForm(request.POST)

          if Fcandidate.is_valid() and Fcandidate_Details.is_valid() :
              password_temp = sha256_crypt.encrypt( Fcandidate_Details.cleaned_data['phone_number'])
              update_Candidate = Candidate(
                                     first_name= Fcandidate.cleaned_data['first_name'],
                                     last_name= Fcandidate.cleaned_data['last_name'],
                                     loginid= Fcandidate_Details.cleaned_data['email_address'],
                                     password= password_temp
                                       )
              update_Candidate.save()
              update_Candidate_Details = Candidate_Details(
                                     candidate  = update_Candidate,
                                     phone_number= Fcandidate_Details.cleaned_data['phone_number'],
                                     education= Fcandidate_Details.cleaned_data['education'],
                                     email_address= Fcandidate_Details.cleaned_data['email_address'],
                                     work_experience= Fcandidate_Details.cleaned_data['work_experience'],
                                     employment_authorization= Fcandidate_Details.cleaned_data['employment_authorization'],
                                     technical_skillset= Fcandidate_Details.cleaned_data['technical_skillset']
                                     )

              update_Candidate_Details.save()
            # -----------------------Email--------------------------------

              token = gen_token(update_Candidate)
              current_site = get_current_site(request)
              message = render_to_string('resumeapp/mail_body.txt', {
              'user': update_Candidate.first_name,
              'domain': current_site.domain,
              'uid': urlsafe_base64_encode(force_bytes(update_Candidate.id)),
              'token': urlsafe_base64_encode(force_bytes(token)),
                })
              email = EmailMessage('Please verify account', message, to=[update_Candidate_Details.email_address])
              email.send()

             # -----------------------Email--------------------------------
              return render(request,'resumeapp/ThankYou.html')
          else:
              context = {'candidate': Fcandidate, 'candidate_Details': Fcandidate_Details}
              return render(request, 'resumeapp/Applicants_Detail.html' , context )




def user_login(request):
    userLoginForm = UserLoginForm()
    return render( request,'resumeapp/my_account.html' , {'form': userLoginForm  } )

def update_password(request):
    if request.method == 'POST':
        if (request.session.has_key('uid')):

            email_check = request.POST['email']
            login_exist = Candidate.objects.filter(loginid=email_check)

            if not login_exist:

                newpass = request.POST['pass1']
                print (len(newpass))
                newencrypt = sha256_crypt.encrypt(str(newpass))
                print (newencrypt)
                resume = Candidate.objects.filter(id=request.session['uid']).update(loginid=request.POST['email'],
                                        password=newencrypt)
                request.session['eid'] = request.POST['email']
                return render(request,'resumeapp/JobSearch.html',{'udata':request.session['eid']})

            else:

                messages.error(request, "Email is already registered", extra_tags='Register')
                return HttpResponseRedirect(reverse('resumeapp:User_Login'))

    else:
        return render(request,'resumeapp/Homepage.html')

def registered_user(request):

    if request.method == 'POST':
        userLoginForm = UserLoginForm(request.POST)

        if userLoginForm.is_valid():
            user_email = userLoginForm.cleaned_data['loginid']
            pass1 = userLoginForm.cleaned_data['password']
            email_exist = Candidate.objects.filter(loginid = user_email,email_active_field = True)

            if email_exist:

                password_exist = Candidate.objects.filter(loginid=user_email).values_list('password',flat=True)
                new_pass = list(password_exist)
                pass2 = (new_pass[0])
                password_check=sha256_crypt.verify(pass1,pass2)

                if email_exist and password_check:
                    request.session['eid'] = user_email
                    return render(request,'resumeapp/Job_Search_Results.html',{'udata': request.session['eid']})
                else:
                    messages.error(request,"Please Use valid Credentials..Incorrect Password",extra_tags='login')
                    return HttpResponseRedirect(reverse('resumeapp:my_account'))
            else:
                messages.info(request,"Please use registered Email to login",extra_tags='register')
                return HttpResponseRedirect(reverse('resumeapp:my_account'))

    return HttpResponseRedirect(reverse('resumeapp:my_account'))

def reset_password(request):
    return render(request,'resumeapp/ResetPassword.html')


def update_reset_password(request):

    if request.method == 'POST':

            email = request.POST['email']
            if Candidate.objects.filter(loginid=request.POST['email']).exists():

                password1 = request.POST['pass1']
                password2 = request.POST['pass2']
                encrypt_pass = sha256_crypt.encrypt(str(password1))

                if password1 == password2:
                    encrypt_pass = sha256_crypt.encrypt(str(password1))
                    s = Candidate.objects.filter(loginid=request.POST['email']).update(password=encrypt_pass)
                    messages.success(request,"Your Password has been updated Successfully.",extra_tags='login')
                    print ("success")
                    return HttpResponseRedirect(reverse('resumeapp:Forgot_Password'))
                else:
                    messages.error(request,"Password doesn't match.Please recheck",extra_tags='Wrong_Password')
                    print ("failure")
                    return HttpResponseRedirect(reverse('resumeapp:Forgot_Password'))
            else:
                messages.error(request,"Please use the registered email Address",extra_tags='Not_Register')
            return HttpResponseRedirect(reverse('resumeapp:Forgot_Password'))


def logout(request):
    if request.session.has_key('eid'):
        print ("IN LOGOUT")
        print (request.session.session_key)
        print (request.session.keys())
        del request.session['eid']
        return HttpResponseRedirect(reverse('resumeapp:Homepage'))

# Diplay the requested list of jobs
def job_list(request,catergory=None, location=None):
    print("in job list")

    start = datetime.now()
    print(start)

    s3_client = boto3.client('s3',
        region_name='us-east-2',
        aws_access_key_id= os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key= os.environ.get('AWS_SECRET_ACCESS_KEY'))
    list_files = []
    theobjects = s3_client.list_objects_v2(Bucket='numpyninja-jobscrapper')
    print(theobjects)

    for object in theobjects["Contents"]:
        file_csv = (object["Key"])
        file_link = ('https://numpyninja-jobscrapper.s3.us-east-2.amazonaws.com/' + file_csv)
        print(file_link)
        list_files.append(file_link)
    print(list_files)

    #pandas.set_option('display.max_columns', None)
    #df_from_each_file = (pandas.read_csv(f) for f in list_files)
    #df_aws = pandas.concat(df_from_each_file, ignore_index=True)
    #print(df_aws.shape)
    #print(df_aws.columns)

    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket='numpyninja-jobscrapper')
    all = response["Contents"]
    latest = max(all, key=lambda x: x['LastModified'])
    latest_file = (latest['Key'])
    print(latest_file)

    if catergory == None and location == None:
        job_category = request.GET.get('jobcategory')
        job_loc = request.GET.get('joblocation')
    else:
        job_category=catergory
        job_loc=location
    print(job_category,job_loc)
    pandas.set_option('display.max_columns', None)

    #Create pandas dataframe of provived csv
    #df_aws = pandas.read_csv('C:\\Users\\rajth\\Desktop\\Jobmonster_Nov5.csv')
    df_aws = pandas.read_csv('https://numpyninja-jobscrapper.s3.us-east-2.amazonaws.com/Jobmonster_Nov5.csv')
    #df_aws = pandas.read_csv('C:\\Users\\rajth\\PycharmProjects\\NumpyNinja_JobPortal\\Resume_Portal\\ResumePortal\\resumeapp\\templates\\resumeapp\\Jobs_Scrapped_new.csv')
    print(df_aws.shape)

    #Search df with Searched Job Location & Job Category
    df = df_aws.query('`Searched Job Location` == @job_loc & `Searched Job Title` == @job_category')

    #Drop Duplicates
    df = df.drop_duplicates(subset=['Job Description'],keep='first')

    #change the column names to lowercase and replace spaces with underscore
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    #print(df)

    # Create new df that shows the jobs with email address and phoneno.s at the beginning

    df1 = pandas.DataFrame()
    df1 = df1.append(df[(df["job_email"] != '[]') | (df["job_phone_no"] != '[]')])
    df1 = df1.append(df[(df["job_email"] == '[]') & (df["job_phone_no"] == '[]')])


    data_dict=df1.to_dict('records')

    #print (data_dict)

    context = {
        'dict' : data_dict,
        'selected_category': job_category,
        'selected_location': job_loc
    }

    end = datetime.now()
    print(end)
    print(end - start)

    return render(request,'resumeapp/Job_Search_Results.html',context)

def send_email(request):
        #job_cat_loc = request.POST.get('selected_category_location')
        #print(job_cat_loc)
        #job_category = "Python/Django Developer"
        #job_loc = "San Francisco"
        #print(job_category, job_loc)
        print("in send_email")
        # Get contacts and message from Json file
        #email_obj = self.json_to_obj(json_file)

        email=request.POST.get('email_list')
        print("email:",email)
        email="['receiver1@gmail.com','receiver2@gmail.com']"
        email_list = email.strip('][').replace("'", "").split(",")

        #email = ["pradeepa.gp@gmail.com"]

        for receiver_email in email_list:
            subject = "Job Application"
            body = " "
            sender_email = "abc@gmail.com"
            # receiver_email = receiver_email

            # provide sender email pwd
            password = "********"


            # Create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject
            # message["Bcc"] = receiver_email  # Recommended for mass emails

            text = """\

                    Hello, \

                    Applying to job\

                    Please find the attached resume for your refernece  \

                    Thank You!! """
            # Add body to email
            message.attach(MIMEText(body, "plain"))
            message.attach(MIMEText(text, "plain"))
            filename = "C:\\Users\\prade\\PycharmProjects\\ResumeParser_Python_Django_App\\ResumePortal\\media\\Geetha.docx"  # In same directory as script

            # Open PDF file in binary mode
            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )

            # Add attachment to message and convert message to string
            message.attach(part)
            text = message.as_string()

            # Log in to server using secure context and send email
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, text)
            print("Email sent successfully to ", receiver_email)
        messages.info(request, "Email successfully sent")

        """
            pandas.set_option('display.max_columns', None)
            df_from_each_file = (pandas.read_csv(f) for f in li)
            df_aws = pandas.concat(df_from_each_file, ignore_index=True)
            print(df_aws.shape)
            print(df_aws.columns)
        """
        #job_list(request,job_category,job_loc)
        return render(request, 'resumeapp/Job_Search.html')

def job_list_new(request,catergory=None, location=None):
    print("in job list")

    start = datetime.now()
    print(start)

    s3_client = boto3.client('s3',
        region_name='us-east-2',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key= os.environ.get('AWS_SECRET_ACCESS_KEY'))
    list_files = []
    theobjects = s3_client.list_objects_v2(Bucket='numpyninja-jobscrapper')
    print(theobjects)

    for object in theobjects["Contents"]:
        file_csv = (object["Key"])
        file_link = ('https://numpyninja-jobscrapper.s3.us-east-2.amazonaws.com/' + file_csv)
        print(file_link)
        list_files.append(file_link)
    print(list_files)

    #pandas.set_option('display.max_columns', None)
    #df_from_each_file = (pandas.read_csv(f) for f in list_files)
    #df_aws = pandas.concat(df_from_each_file, ignore_index=True)
    #print(df_aws.shape)
    #print(df_aws.columns)

    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket='numpyninja-jobscrapper')
    all = response["Contents"]
    latest = max(all, key=lambda x: x['LastModified'])
    latest_file = (latest['Key'])
    print(latest_file)






    #try:
        #s3_client.download_file('numpyninja-jobscrapper','Jobmonster_Nov5.csv', 'C:\\Users\\rajth\\PycharmProjects\\NumpyNinja_JobPortal\\Resume_Portal\\ResumePortal\\Csvfiles\\file.csv')

    #except botocore.exceptions.ClientError as e:
        #if e.response['Error']['Code'] == "404":
            #print("The object does not exist.")
        #else:
            #raise

    #list_of_files = glob.glob(file_location)
    #latest_file = max(list_of_files, key=os.path.getctime)
    #print(latest_file)



    if catergory == None and location == None:
        job_category = request.GET.get('jobcategory')
        job_loc = request.GET.get('joblocation')
    else:
        job_category=catergory
        job_loc=location
    print(job_category,job_loc)
    pandas.set_option('display.max_columns', None)

    #Create pandas dataframe of provived csv
    #df_aws = pandas.read_csv('C:\\Users\\rajth\\Desktop\\Jobmonster_Nov5.csv')
    cols = ['Searched Job Location','Searched Job Title','Job Title','Job Location','Company Name','Job Phone No','Job Email','Job Link','Job Description']
    df_aws = pandas.read_csv('https://numpyninja-jobscrapper.s3.us-east-2.amazonaws.com/Jobmonster_Nov5.csv',usecols=cols)
    #df_aws = pandas.read_csv('C:\\Users\\rajth\\PycharmProjects\\NumpyNinja_JobPortal\\Resume_Portal\\ResumePortal\\resumeapp\\templates\\resumeapp\\Jobs_Scrapped_new.csv')
    print(df_aws.shape)

    #Search df with Searched Job Location & Job Category
    df = df_aws.query('`Searched Job Location` == @job_loc & `Searched Job Title` == @job_category')

    #Drop Duplicates
    df = df.drop_duplicates(subset=['Job Description'],keep='first')

    #change the column names to lowercase and replace spaces with underscore
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    print(df)

    # Create new df that shows the jobs with email address and phoneno.s at the beginning
    df1 = pandas.DataFrame()
    df1 = df1.append(df[(df["job_email"] != '[]') | (df["job_phone_no"] != '[]')])
    df1 = df1.append(df[(df["job_email"] == '[]') & (df["job_phone_no"] == '[]')])

    #data_dict=df1.to_dict('records')

    data_dict = df_aws.to_dict('records')

    print (data_dict)

    context = {
        'dict' : data_dict,
        'selected_category': job_category,
        'selected_location': job_loc
    }

    end = datetime.now()
    print(end)
    print(end - start)

    return render(request,'resumeapp/Job_Search_Results.html',context)



def job_list_db(request):

    if request.method == 'POST':
        job_category = request.POST['sjobcategory']
        job_loc = request.POST['sjoblocation']
        new_job_category = job_category.split()
        keyword = "Python"

        if keyword in new_job_category:
            job_search = Job_Details.objects.filter(searched_job_title__startswith = keyword, searched_job_location=job_loc)
        else:
            job_search = Job_Details.objects.filter(searched_job_title=job_category, searched_job_location=job_loc)

        list_job = [entry for entry in job_search.values()]
        res = defaultdict(list)
        for sub in list_job:
            for key in sub:
                res[key].append(sub[key])
        job_list_dict = dict(res)
        postbacks = "Yes"
    else:
        list_job = list()
        job_category = ""
        job_loc = ""
        postbacks = "Not"
    'Converting Queryset to list'

        # sorted_dict =  (sorted(list_job, key=lambda i: (i['job_email'],i['job_phone_no'])))
    'Converting List to Dictionary'

    # print (type(job_list_dict))

    context = {
        'dict': list_job,
        'selected_category': job_category,
        'selected_location': job_loc,
        'postbacks':postbacks,
        'udata':request.session['eid']
    }

    return render(request, 'resumeapp/Job_Search_Results.html', context)

#-----------------------Email--------------------------------

def check_token(user, token):

    generatedtokenstr = gen_token_str(user)

    resultcomp = sha256_crypt.verify( generatedtokenstr ,  token )
    return  resultcomp

def gen_token_str(user):

    strtoen = six.text_type(user.pk) + six.text_type(user.loginid) + six.text_type(
        user.email_active_field)
    return strtoen

def gen_token(user):

    strtoen = six.text_type(user.pk) + six.text_type(user.loginid) + six.text_type(
        user.email_active_field)

    str1 = sha256_crypt.encrypt( strtoen )
    # str11 = urlsafe_base64_encode(str1)
    return str1


def activate(request, uidb64, token):
    try:
        token_no64 = urlsafe_base64_decode(token).decode()
        uid =  urlsafe_base64_decode(uidb64).decode()
        user = models.Candidate.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and check_token(user, token_no64):
        user. email_active_field = True
        user.save()
        messages.error(request, "Thank you for your email confirmation. Now you can login to your account", extra_tags='login')
        return HttpResponseRedirect(reverse('resumeapp:my_account'))
    else:
       messages.error(request, "Activation link is invalid!", extra_tags='login')
       return HttpResponseRedirect(reverse('resumeapp:my_account'))


#-----------------------Email--------------------------------