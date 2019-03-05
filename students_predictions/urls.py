from django.conf.urls import url, include
from rest_framework import routers
from students_predictions import views

urlpatterns = [
    url(r'predict_survey',views.predict_survey,name='predict_survey'),
    url(r'train_survey',views.train_survey,name='train_survey')
]
