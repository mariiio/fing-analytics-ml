# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.shortcuts import render

# # Create your views here.
# from django.http import HttpResponse

# def index(request):
#     return HttpResponse("Hello, Fing.")

from django.http import JsonResponse
from students_predictions.predictions import predict_student_survey, train_survey_model, predict_student_course, train_course_model

# SURVEY
def predict_survey(request):
  ci = request.GET.get('ci', None)

  data = {
    "result": {
      "ci": ci,
      "prediction": {2: 'Recursa', 1: 'Derecho a examen', 0: 'Exonera'}[predict_student_survey(ci)[0]]
    }
  }
  return JsonResponse(data)

def train_survey(request):
    train_survey_model()
    return JsonResponse({"message": "The model has been trained successfully"})

# COURSE
def predict_course(request):
  ci = request.GET.get('ci', None)

  data = {
    "result": {
      "ci": ci,
      "prediction": {2: 'Recursa', 1: 'Derecho a examen', 0: 'Exonera'}[predict_student_course(ci)[0]]
    }
  }
  return JsonResponse(data)

def train_course(request):
    train_course_model()
    return JsonResponse({"message": "The model has been trained successfully"})
