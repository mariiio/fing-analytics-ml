# -*- coding: utf-8 -*-
from sklearn import tree
import graphviz
from sklearn import metrics
import pickle
from students_predictions.models import StudentSurvey

def mapData(student):
    return [mapAge(student[3]), mapOrigin(student[4]),
    mapEducation(student[5]), mapWork(student[6]),
    mapWorkRelated(student[7]), mapCount(student[8]),
    mapReTake(student[9]), mapAsistance(student[10]),
    mapAsistance(student[11]), mapGroup(student[12]),
    mapTimeDedicated(student[13]), mapMotivation(student[14])]

def mapDataObject(student):
    return [mapAge(student.age), mapOrigin(student.location),
    mapEducation(student.education), mapWork(student.works),
    mapWorkRelated(student.works_related), mapCount(student.semester_subjects_count),
    mapReTake(student.course_take_count), mapAsistance(student.assists_theoretical),
    mapAsistance(student.assists_practical), mapGroup(student.study_method),
    mapTimeDedicated(student.study_hours), mapMotivation(student.motivation_level)]

def mapAge(x):
    return {'25 o más': 2, '21-24 años': 1, '18-20 años': 0}[x.encode("utf8")]


def mapOrigin(x):
    return {'Montevideo': 1, 'Interior': 0}[x]


def mapEducation(x):
    return {'Privada': 2, 'Pública': 1, 'U.T.U.': 0}[x.encode("utf8")]


def mapWork(x):
    return {'Si, Full-Time': 2, 'Si, Part-Time': 1, 'No': 0}[x]


def mapWorkRelated(x):
    return {1: 1, 0: 0}[x]


def mapCount(x):
    return {5: 4, 4: 3, 3: 2, 2: 1, 1: 0}[x]


def mapReTake(x):
    return {'Más de dos': 2, 'Dos': 1, 'Una': 0}[x.encode("utf8")]


def mapAsistance(x):
    return {'Sí': 2, 'A veces': 1, 'No': 0}[x.encode("utf8")]


def mapGroup(x):
    return {'Solo;En grupo': 2, 'Solo': 1, 'En grupo': 0}[x]


def mapTimeDedicated(x):
    return {'3 o menos': 2, 'Entre 3 y 6': 1, '6 o más': 0}[x.encode("utf8")]


def mapMotivation(x):
    return {'Bajo': 2, 'Medio': 1, 'Alto': 0}[x]


def mapResult(x):
    return {'Recursé': 2, 'Derecho a examen': 1, 'Exoneré': 0}[x.encode("utf8")]

def train():
  x_train = []
  y_train = []
  trainData = list(StudentSurvey.objects.values_list())

  for row in trainData:
      x_train.append(mapData(row))
      y_train.append(mapResult(row[15]))

  classifier = tree.DecisionTreeClassifier(criterion="entropy", max_depth=10)
  save_model(classifier.fit(x_train, y_train))

def predict(ci):
  student = StudentSurvey.objects.get(ci=ci)
  return retrieve_model().predict([mapDataObject(student)])

def save_model(classifier):
  file = open('storedModel', 'w')
  pickle.dump(classifier, file)
  file.close()

def retrieve_model():
  file = open('storedModel', 'r')
  return pickle.load(file)
