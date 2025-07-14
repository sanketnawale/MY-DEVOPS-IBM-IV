"""
URL configuration for jobfrontend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from jobs import views
from django.shortcuts import redirect  
from jobs.views import send_spool_to_ollama  # Import function


urlpatterns = [
    path('admin/', admin.site.urls),
    path('jobs/', views.job_list, name='job_list'),
    path('', lambda request: redirect('job_list')),
    path('jobs/<str:jobid>/spool/', views.view_spool, name='view_spool'),
    path('send_spool/', views.send_spool_to_ollama, name='send_spool'),

]



