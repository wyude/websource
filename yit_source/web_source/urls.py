"""myproject URL Configuration

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
from django.urls import path, re_path
from .controller import views

app_name = 'web_source'
urlpatterns = [

    path('', views.index, name='index'),
    path('/', views.index, name='index'),
    #path('login', views.login, name='login'),
    #path('logout', views.logout, name='logout'),
    path('index', views.index, name='index'),
    path('searchip', views.searchip, name='searchip'),
    path('map', views.map, name='map'),
    path('map_online', views.map_online, name='map_online'),
    path('caccenter', views.cacCenter, name='caccenter'),
    path('wells', views.wells, name='wells'),
    path('paths', views.paths, name='paths'),
    path('update_status', views.update_status, name='update_status'),


]
