"""ControllerVisualizer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from UploadData.views import *
from Visualization.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',data_upload, name='home'),
    path('upload/', data_upload, name="data_upload"),
    path('visualization/<str:fid>/', visualization, name="visualization"),
    path('data-list/',get_all_files, name='get_all_files'),
    path('delete/<str:fid>/', delete_file, name="delete_file"),
]
