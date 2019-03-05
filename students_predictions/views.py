# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.shortcuts import render

# # Create your views here.
# from django.http import HttpResponse

# def index(request):
#     return HttpResponse("Hello, Fing.")

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from students_predictions.models import StudentSurvey
from students_predictions.predictions import predict, train

def predict_survey(request):
  ci = request.GET.get('ci', None)
  student_survey = get_object_or_404(StudentSurvey, ci=ci)

  data = {
    "result": {
      "ci": student_survey.ci,
      "prediction": {2: 'Recursa', 1: 'Derecho a examen', 0: 'Exonera'}[predict(student_survey.ci)[0]]
    }
  }
  return JsonResponse(data)

def train_survey(request):
    train()
    return JsonResponse({"message": "The model has been trained successfully"})
