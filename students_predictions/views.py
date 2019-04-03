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
  model = request.GET.get('model', 'error')
  tree_path = "{0}.png".format(model)
  image_data = open(tree_path, "rb").read()
  return HttpResponse(image_data, content_type="image/png")
