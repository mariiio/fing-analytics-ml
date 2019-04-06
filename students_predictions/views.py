# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import JsonResponse, HttpResponse
from students_predictions.predictions import train, predict

def train_models(request):
  train()
  return JsonResponse({"message": "The model has been trained successfully"})

def predict_students(request):
  predict()
  return JsonResponse({"message": "The predictions are ready"})

def model_tree(request):
  courseDetailId = request.GET.get('student')
  modelName = request.GET.get('model')

  filePath = ""
  if courseDetailId is not None:
    filePath = "models_output/{0}_predictionTree.png".format(courseDetailId)
  elif modelName is not None:
    filePath = "models_output/{0}.png".format(modelName)  

  try:
    image_data = open(filePath, "rb").read()
    return HttpResponse(image_data, content_type="image/png")
  except:
    return HttpResponse("", content_type="text")
  
