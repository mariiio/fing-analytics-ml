from django.conf.urls import url, include
from rest_framework import routers
from students_predictions import views

urlpatterns = [
    url(r'predict_students',views.predict_students,name='predict_students'),
    url(r'train_models',views.train_models,name='train_models')
]
