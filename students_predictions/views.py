# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse, HttpResponse
from students_predictions.predictions import train, predict, getModelTree

def train_models(request):
  train()
  return JsonResponse({"message": "The model has been trained successfully"})

def predict_students(request):
  predict()
  return JsonResponse({"message": "The predictions are ready"})

def model_tree(request):
  courseDetailId = request.GET.get('student')
  modelName = request.GET.get('model')

  return getModelTree(courseDetailId, modelName)
