# -*- coding: utf-8 -*-
from sklearn import tree
import graphviz
from sklearn import metrics
import pickle
from students_predictions.models import *
import django.utils.timezone as tz
import re
from pydot import Dot, Edge
import pydot


def getValues(symbol, value):
    j = range(int(float(value))+1)
    if symbol == '<':
        return sorted(i for i in j if i < value)
    if symbol == '<=':
        return sorted(i for i in j if i <= value)
    if symbol == '=':
        return [value]
    if symbol == '>':
        return sorted(i for i in j if i > value)
    if symbol == '>=':
        return sorted(i for i in j if i >= value)


def mapAge(age):
    return {'25 o más': 2, '21-24 años': 1, '18-20 años': 0}[age]


def mapAgeInv(value):
    return {2: '25 o más', 1: '21-24 años', 0: '18-20 años'}[value]


def mapOrigin(loc):
    return {'Montevideo': 1, 'Interior': 0}[loc]


def mapOriginInv(loc):
    return {1: 'Montevideo', 0: 'Interior'}[loc]


def mapEducation(x):
    return {'Privada': 2, 'Pública': 1, 'U.T.U.': 0}[x]


def mapEducationInv(x):
    return {2: 'Privada', 1: 'Pública', 0: 'U.T.U.'}[x]


def mapWork(x):
    return {'Si, Full-Time': 2, 'Si, Part-Time': 1, 'No': 0}[x]


def mapWorkInv(x):
    return {2: 'Si, Full-Time', 1: 'Si, Part-Time', 0: 'No'}[x]


def mapWorkRelated(x):
    return {1: 1, 0: 0}[x]


def mapWorkRelatedInv(x):
    return {1: 'Si', 0: 'No'}[x]


def mapCount(x):
    return {5: 4, 4: 3, 3: 2, 2: 1, 1: 0}[x]


def mapReTake(x):
    return {'Tres': 2, 'Dos': 1, 'Una': 0}[x]


def mapAsistance(x):
    return {'Sí': 2, 'A veces': 1, 'No': 0}[x]


def mapAsistanceInv(x):
    return {2: 'Sí', 1: 'A veces', 0: 'No'}[x]


def mapGroup(x):
    return {'Solo;En grupo': 2, 'Solo': 1, 'En grupo': 0}[x]


def mapGroupInv(x):
    return {2: 'Solo;En grupo', 1: 'Solo', 0: 'En grupo'}[x]


def mapTimeDedicated(x):
    return {'3 o menos': 2, 'Entre 3 y 6': 1, '6 o más': 0}[x]


def mapTimeDedicatedInv(x):
    return {2: '3 o menos', 1: 'Entre 3 y 6', 0: '6 o más'}[x]


def mapMotivation(x):
    return {'Bajo': 2, 'Medio': 1, 'Alto': 0}[x]


def mapMotivationInv(x):
    return {2: 'Bajo', 1: 'Medio', 0: 'Alto'}[x]


def mapRule(r):
    r = r.replace('Asistencia teoricos', 'Asistencia-teoricos')
    r = r.replace('Asistencia practicos', 'Asistencia-practicos')
    r = r.replace('Tiempo dedicado', 'Tiempo-dedicado')
    r = r.replace('Trabajo software', 'Trabajo-software')
    rule = r.split(' ')
    name = rule[0]
    op = rule[1]
    value = rule[2]
    if re.search('Edad', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapAgeInv(x))
        seperator = ' o '
        return 'Edad = ' + seperator.join(conditions)
    if re.search('Origen', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapOriginInv(x))
        seperator = ' o '
        return 'Origen = ' + seperator.join(conditions)
    if re.search('Educacion', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapEducationInv(x))
        seperator = ' o '
        return 'Educacion = ' + seperator.join(conditions)
    if re.search('Trabajo', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapWorkInv(x))
        seperator = ' o '
        return 'Trabajo = ' + seperator.join(conditions)
    if re.search('Trabajo-software', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapWorkRelated(x))
        seperator = ' o '
        return 'Trabajo software = ' + seperator.join(conditions)
    if re.search('Asistencia-teoricos', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapAsistanceInv(x))
        seperator = ' o '
        return 'Asistencia teoricos = ' + seperator.join(conditions)
    if re.search('Asistencia-practicos', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapAsistanceInv(x))
        seperator = ' o '
        return 'Asistencia practicos = ' + seperator.join(conditions)
    if re.search('Grupo', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapGroupInv(x))
        seperator = ' o '
        return 'Estudio = ' + seperator.join(conditions)
    if re.search('Tiempo-dedicado', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapTimeDedicatedInv(x))
        seperator = ' o '
        return 'Tiempo dedicado = ' + seperator.join(conditions)
    if re.search('Motivacion', name):
        conditions = []
        for x in getValues(op, value):
            conditions.append(mapMotivationInv(x))
        seperator = ' o '
        print(conditions)
        return 'Motivacion = ' + seperator.join(conditions)
    return r


def retrieve_model(model_name):
    file = open('models_output/' + model_name, 'r')
    return pickle.load(file)


def mapLabels(labels):
    isLeaf = re.search('value', labels[0])
    if isLeaf and len(labels) > 1:
        newLabels = []
        newLabels.append(labels[0].replace('value', 'P'))
        newLabels.append(labels[1].replace('class', 'Clase').replace('"', ''))
        return newLabels
    if len(labels) > 2:
        newLabels = []
        newLabels.append(mapRule(labels[0]).replace('"', ''))
        newLabels.append(labels[1].replace('value', 'P'))
        newLabels.append(labels[2].replace('class', 'Clase').replace('"', ''))
        return newLabels
    return labels


def getFeaturesNames(modelName):
    labels = ['Lab1', 'Lab2']
    hasLogs = re.search('Logs', modelName)
    hasSurvey = re.search('Survey', modelName)
    isModel2 = re.search('Model2', modelName)
    isModel3 = re.search('Model3', modelName)
    isModel4 = re.search('Model4', modelName)
    if isModel2 or isModel3 or isModel4:
        labels.append('Test1')
    if isModel3 or isModel4:
        labels.append('Lab 3')
    if isModel4:
        labels.append('Lab 4')
    if hasLogs:
        labels = labels + ['Accesos', 'Actividad foro', 'Acceso archivos']
    if hasSurvey:
        labels = labels + [
            'Edad', 'Origen', 'Educacion', 'Trabajo',
            'Trabajo software', 'Cantidad materias', 'Recursadas',
            'Motivacion', 'Asistencia teoricos', 'Asistencia practicos',
            'Grupo', 'Tiempo dedicado'
        ]
    return labels


def getPredictedColor(x):
    if x == 0:
        return 'green'
    if x == 1:
        return 'yellow'
    if x == 2:
        return 'red'


def formatTree(nodes):
    if len(nodes) > 2:
        for i in range(len(nodes)):
            oldLabel = nodes[i].get('label')
            if oldLabel <> None:
                oldLabelArray = oldLabel.split('\\n')
                result = [a for a in oldLabelArray if not re.search(
                    'gini', a) and not re.search('samples', a)]
                result = mapLabels(result)
                seperator = '\\n'
                newLabel = seperator.join(result)
                label = newLabel.decode('utf-8', "replace")
                nodes[i].set_fillcolor('#f5f5dc')
                nodes[i].set_label(label)


def exportTree(modelName):
    clf = retrieve_model(modelName)
    featuresNames = getFeaturesNames(modelName)
    print(featuresNames)
    dot_data = tree.export_graphviz(
        clf, proportion='true', out_file=None, feature_names=featuresNames, class_names=['Exonera', 'Derecho a examen', 'Recursa'], filled=True, rounded=True)
    graphs = pydot.graph_from_dot_data(dot_data)
    nodes = graphs[0].get_nodes()
    formatTree(nodes)
    graphs[0].write_png('models_output/' + modelName + '.png')


def savePredictionTree(studentId, studentMapped, modelName, prediction):
    model = retrieve_model(modelName)
    dot_data = tree.export_graphviz(model, proportion='true', out_file=None,
                                    feature_names=getFeaturesNames(modelName), class_names=['Exonera', 'Derecho a examen', 'Recursa'], filled=True, rounded=True)
    graphs = pydot.graph_from_dot_data(dot_data)
    nodes = graphs[0].get_nodes()
    formatTree(nodes)
    predictedColor = getPredictedColor(prediction)
    node_indicator = model.decision_path(studentMapped)
    decision_path = node_indicator.toarray()[0]
    print(decision_path)
    for node in nodes:
        name = node.get_name()
        if name <> 'node' and name <> 'edge':
            index = int(node.get_name())
            if index < len(decision_path) and decision_path[index] > 0:
                node.set_fillcolor(predictedColor)
    graphs[0].write_png('models_output/' +
                        str(studentId) + '_predictionTree.png')
