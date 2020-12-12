from django.conf.urls import url
from django.contrib import admin
from .import views
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

app_name = 'resumeapp'

urlpatterns =[
    path('', views.upload_page,name='Homepage'),
    path('ApplicantDetails/', views.applicant_file,name='ApplicantDetails'),
    path('Update/',views.update_db,name = 'Update'),
    path('User/',views.user_login,name = 'User_Login'),
    path('Updatepassword/',views.update_password,name ='Password_Update'),
    path('Password/',views.reset_password,name='Forgot_Password'),
    path('Registereduser/',views.registered_user,name = 'Registered_User'),
    path('password/resetpass/',views.update_reset_password,name='Password_Reset'),
    path('Logout/', views.logout, name='Logout'),
    path('JobList/', views.job_list_db, name='JobList'),
    path('JobSearch', views.job_search, name='job-search'),
    url(r'^Thankyou', views.update_db,name='upload-page3'),
    url(r'^JobSearch', views.job_search, name='job-search'),

    url(r'^SendEmail', views.send_email, name='send-email'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)