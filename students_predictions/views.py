# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.shortcuts import render

# # Create your views here.
# from django.http import HttpResponse

# def index(request):
#     return HttpResponse("Hello, Fing.")

from students_predictions.models import StudentSurvey
from rest_framework import viewsets
from students_predictions.serializers import StudentSurveySerializer


class StudentSurveyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students surveys to be viewed or edited.
    """
    queryset = StudentSurvey.objects.all().order_by('-result')
    serializer_class = StudentSurveySerializer
