# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 12:04:38 2019

@author: ayaka
"""

from django.urls import path

from . import views

app_name = 'NoiseBudgetter'
urlpatterns = [
    path('', views.index, name='index'),
    path('addTheoNoise/',views.addTheoNoise,name='addTheoNoise'),
    path('addRTNoise/',views.addRTNoise,name='addRTNoise'),
    path('New/',views.New,name='New'),
    path('savefile/',views.savefile,name='savefile'),
    path('loadfile/',views.loadfile,name='loadfile'),
    path('OnDelete/',views.OnDelete,name='OnDelete'),
    path('plot/',views.plot,name='plot'),
    path('manual/',views.manual,name='manual'),
    path('Categorize/',views.Categorize,name='Categorize'),
    path('UnCategorize/',views.UnCategorize,name='UnCategorize'),
    path('plot_Subplot/',views.plot_Subplot,name='plot_Subplot'),
]
