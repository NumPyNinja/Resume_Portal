# -*- coding: utf-8 -*-
import glob
import pandas
from . import models
import docx
import os
from docx import Document
import json
from .models import Resume
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from pyresparser import ResumeParser
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib import messages
# Open upload page
def upload_page(request):
    print ("First Page")
    return render(request, 'resumeapp/Upload_Screen.html')

#Open job search page
def job_search(request):
    print ("Job Search Page")
    return render(request, 'resumeapp/Job_Search.html')

#Open  the applicant details page
def applicant_file(request):
    print ("Second Page ")

    if request.method== 'POST':
        #Get the uploaded file
        fileuploaded = request.FILES['file1']
        fs = FileSystemStorage()
        fs.save(fileuploaded.name, fileuploaded)

        list_of_files = glob.glob(
            'C:\\Users\\prade\\PycharmProjects\\ResumePortal\\media\\*')  # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)

        # Parse the uploaded resume
        parsed_details = ResumeParser(latest_file).get_extracted_data()
        print(parsed_details)
        resume_dict =  parsed_details

        # Converting to JSON
        loaded_json = json.loads(json.dumps(resume_dict))
        print(loaded_json)

        # converting into .JSON file for .HTML
        with open('C:\\Users\\prade\\PycharmProjects\\ResumePortal\\resumeapp\\templates\\resumeapp\\Resume_details.json',
                  'w') as fp:
            json.dump(loaded_json, fp)
        return render(request, 'resumeapp/Applicant_Screen.html')

#Getparsed Details from second page and store in DB
def uploaded_to_db(request):
    print ("Third Page ..")

    #Get parsed details from applicant page
    if request.method=='POST':
        fn = request.POST.get('name')
        ln = request.POST.get('lname')
        add = request.POST.get('addr')
        ph = request.POST.get('mobile_number')
        email = request.POST.get('email')
        edu = request.POST.get('degree')
        tech = request.POST.get('skills')
        wrk = request.POST.get('total_experience')
        emp = request.POST.get('visa_status')

        #Create new record
        newRecord = Resume(first_name=fn, last_name=ln, address=add, phone_number=ph, email_address=email,
                           education=edu, technical_skillset=tech, work_experience=wrk, employment_authorization=emp)
        #Save the new record in DB
        newRecord.save()

        return render(request, 'resumeapp/ThankYou_Screen.html')

# Diplay the requested list of jobs
def job_list(request,catergory=None, location=None):
    print("in job list")
    if catergory == None and location == None:
        job_category = request.GET.get('jobcategory')
        job_loc = request.GET.get('joblocation')
    else:
        job_category=catergory
        job_loc=location
    print(job_category,job_loc)
    pandas.set_option('display.max_columns', None)

    #Create pandas dataframe of provived csv
    df = pandas.read_csv('resumeapp\\templates\\resumeapp\\Jobs_Scrapped.csv')
    print(df.shape)

    #Search df with Searched Job Location & Job Category
    df = df.query('`Searched Job Location` == @job_loc & `Job Category` == @job_category')

    #Drop Duplicates
    df = df.drop_duplicates(subset=['Company Name'])

    #change the column names to lowercase and replace spaces with underscore
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    #print(df)

    # Create new df that shows the jobs with email address and phoneno.s at the beginning
    df1 = pandas.DataFrame()
    df1 = df1.append(df[(df["job_email"].notnull()) | (df["job_phone_no"].notnull())])
    df1 = df1.append(df[(df["job_email"].isnull()) & (df["job_phone_no"].isnull())])

    data_dict=df1.to_dict('records')

    context = {
        'dict' : data_dict,
        'selected_category': job_category,
        'selected_location': job_loc
    }

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
        email="['pradeepa.gp@gmail.com','rajthilakam@gmail.com']"
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
        #job_list(request,job_category,job_loc)
        return render(request, 'resumeapp/Job_Search.html')