# -*- coding: utf-8 -*-
import graphviz
import pickle
import django.utils.timezone as tz

from joblib import Parallel, delayed
import multiprocessing as mp

from sklearn import tree, metrics
from students_predictions.models import *
from treebuilder import exportTree, savePredictionTree

def mapStudent(student, model_number):
    maped_student = [
        mapAssignment(student.Assignment1),
        mapAssignment(student.Assignment2)
    ]
    if model_number > 1:
        maped_student = maped_student + [mapTest(student.Test1)]
    if model_number > 2:
        maped_student = maped_student + [mapAssignment(student.Assignment3)]
    if model_number > 3:
        maped_student = maped_student + [mapAssignment(student.Assignment4)]

    if has_logs(student):
        maped_student = maped_student + mapLogs(student)
    if completed_survey(student):
        maped_student = maped_student + mapSurvey(student)

    return maped_student


def mapLogs(student):
    return [
        mapAccessCount(student.AccessCount),
        mapForumActivityCount(student.ForumActivityCount),
        mapFileAccessCount(student.FileAccessCount)
    ]


def mapSurvey(student):
    return [
        mapAge(student.Age),
        mapOrigin(student.Location),
        mapEducation(student.Education),
        mapWork(student.Works),
        mapWorkRelated(student.WorksRelated),
        mapCount(student.SemesterSubjectsCount),
        mapReTake(student.CourseTakeCount),
        mapMotivation(student.MotivationLevel),
        mapAsistance(student.AssistsTheoretical),
        mapAsistance(student.AssistsPractical),
        mapGroup(student.StudyMethod),
        mapTimeDedicated(student.StudyHours)
    ]

def mapAge(x):
    return {'25 o más': 2, '21-24 años': 1, '18-20 años': 0}[x.encode("utf8")]

def mapOrigin(x):
    return {'Montevideo': 1, 'Interior': 0}[x]

def mapEducation(x):
    return {'Privada': 2, 'Pública': 1, 'U.T.U.': 0}[x.encode("utf8")]

def mapWork(x):
    return {'Si, Full-Time': 2, 'Si, Part-Time': 1, 'No': 0}[x]

def mapWorkRelated(x):
    return {'Si': 1, 'No': 0, '': 0}[x]

def mapCount(x):
    return {5: 4, 4: 3, 3: 2, 2: 1, 1: 0}[x]

def mapReTake(x):
    return {'Más de dos': 3, 'Dos': 2, 'Una': 1, '': 0}[x.encode("utf8")]

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

def mapTest(x):
    if x == '':
        return 0
    return int(x)
    if not x or 0 <= int(x) <= 24:
        return 2
    elif 25 <= int(x) <= 59:
        return 1
    return 0

def mapAssignment(x):
    if x == '':
        return 0
    return int(x)
    if 0 <= int(x) <= 64:
        return 2
    elif 65 <= int(x) <= 89:
        return 1
    return 0

# TODO: DEFINIR RANGOS

def mapAccessCount(x):
    return int(x)
    if 0 <= int(x) <= 64:
        return 2
    elif 65 <= int(x) <= 89:
        return 1
    return 0

def mapForumActivityCount(x):
    return int(x)
    if 0 <= int(x) <= 64:
        return 2
    elif 65 <= int(x) <= 89:
        return 1
    return 0

def mapFileAccessCount(x):
    return int(x)
    if 0 <= int(x) <= 64:
        return 2
    elif 65 <= int(x) <= 89:
        return 1
    return 0

def mapFinalResult(x):
    if 0 <= int(x) <= 2:
        return 2
    elif 3 <= int(x) <= 5:
        return 1
    return 0

def train():
    baseQuery = model_base_query()
    students = Student.objects.raw(baseQuery + " and grades.Final is not null")
    
    x_train_dict = {}
    y_train_dict = {}
    classifier = tree.DecisionTreeClassifier(criterion="gini", splitter='best', min_samples_leaf=3, max_depth=5)
    
    for student in students:
        for model_number in range(1, 5):
            modelName = model_name(model_number, student)

            studentMap = mapStudent(student, model_number)
            if x_train_dict.has_key(modelName):
                x_train_dict[modelName].append(studentMap)
            else:
                x_train_dict[modelName] = [studentMap]

            resultMap = mapFinalResult(student.Final)
            if y_train_dict.has_key(modelName):
                y_train_dict[modelName].append(resultMap)
            else:
                y_train_dict[modelName] = [resultMap]

    for modelName in x_train_dict.keys():
        trainModel = x_train_dict[modelName]
        predictionModel = y_train_dict[modelName]
        if len(trainModel) > 0:
            save_model(classifier.fit(trainModel, predictionModel), modelName)
            exportTree(modelName)
            print("Model " + modelName  + " trained succesfully")

def predict():
    baseQuery = model_base_query()
    students = Student.objects.raw(baseQuery + " and grades.Final is null")
    
    # Create pool
    c = mp.cpu_count()
    pool = mp.Pool(c)

    # Call parallel for
    results = [pool.apply_async(predictStudent, args=(student,)) for student in students]

    # Wait for all threads to finish
    pool.close()
    pool.join()


def predictStudent(student):
    modelNumber = model_number(student)
    modelName = model_name(modelNumber, student)
    modelFile = retrieve_model(modelName)
    
    if modelFile is None:
        return

    studentMap = mapStudent(student, modelNumber)
    prediction = modelFile.predict([studentMap])[0]
    predictionResult = {2: 'FAIL', 1: 'EXAM', 0: 'PASS'}[prediction]    

    Prediction(CourseDetailId=student.id, Result=predictionResult, Timestamp=tz.localtime()).save()
    savePredictionTree(student.id, [studentMap], modelName, prediction)
    print("Student " + str(student.id) + " predicted succesfully.")

def model_base_query():
  return '''
  SELECT distinct(grades.Id) as id, grades.Year,
	       student_logs.AccessCount, student_logs.ForumActivityCount, student_logs.SurveyResponseCount, student_logs.FileAccessCount,
         s.Age, s.Location, s.Education,s.Works,s.WorksRelated,s.SemesterSubjectsCount,s.CourseTakeCount,
         s.AssistsTheoretical, s.AssistsPractical, s.StudyMethod, s.StudyHours, s.MotivationLevel,
         grades.Test1, grades.Test2, grades.Assignment1, grades.Assignment2, grades.Assignment3, grades.Assignment4, grades.Assignment5, grades.Final
  from
  (
    select cd.Id, s.Name, c.year as Year,
      min(case when t.Name like "%%Primer Parcial%%" then ar.Result else null end) as Test1,
      min(case when t.Name like "%%Segundo Parcial%%" then ar.Result else null end) as Test2,
      min(case when a.Name like "%%tarea 1%%" then ar.Result else null end) as Assignment1,
      min(case when a.Name like "%%tarea 2%%" then ar.Result else null end) as Assignment2,
      min(case when a.Name like "%%tarea 3%%" then ar.Result else null end) as Assignment3,
      min(case when a.Name like "%%tarea 4%%" then ar.Result else null end) as Assignment4,
      min(case when a.Name like "%%tarea 5%%" then ar.Result else null end) as Assignment5,
      min(case when f.Name like "%%Nota Final%%" then ar.Result else null end) as Final
      from
      course_details cd inner join
      courses c on cd.CourseId = c.Id inner join
      activity_results ar on cd.Id = ar.CourseDetailId inner join
      students s on cd.StudentId = s.Id
      left outer join tests t on ar.TestId = t.Id
      left outer join finals f on ar.FinalId = f.Id
      left outer join assignments a on ar.AssignmentId = a.Id
    group by S.Name, c.year, cd.Id
  ) grades
  left outer join
  (
    select log_action.Id, log_action.Year,
    max(case when log_action.Action like "%%ACCESS%%" then log_action.count else 0 end) as AccessCount,
    max(case when log_action.Action like "%%FORUM_ACTIVITY%%" then log_action.count else 0 end) as ForumActivityCount,
    max(case when log_action.Action like "%%SURVEY_RESPONSE%%" then log_action.count else 0 end) as SurveyResponseCount,
    max(case when log_action.Action like "%%FILE_ACCESS%%" then log_action.count else 0 end) as FileAccessCount
    from (
      select Id, Action, Year, avg(count) as count from (
        select cd.Id, l.Action, c.Year, WEEKOFYEAR(l.Timestamp) as week, count(*) as count
          from logs l
          inner join course_details cd on l.CourseDetailId = cd.Id
          inner join students s on cd.StudentId = s.Id
          inner join courses c on cd.CourseId = c.Id
        group by action, cd.Id, c.Year, week
        ) week_avg
      group by Id, Action, Year
    ) log_action
    group by Id
  ) student_logs on grades.Id = student_logs.Id and grades.Year = student_logs.Year
  left outer join
    student_surveys s on grades.Id = s.CourseDetailId
    where grades.Assignment2 != ""
  '''

def save_model(classifier, model_name):
    file = open('models_output/' + model_name, 'w')
    pickle.dump(classifier, file)
    file.close()

def retrieve_model(model_name):
    try:
        file = open('models_output/' + model_name, 'r')
        return pickle.load(file)
    except:
        return None

def model_number(student):
    if student.Assignment4:
        return 4
    elif student.Assignment3:
        return 3
    elif student.Test1:
        return 2
    else:
        return 1

def model_name(model_number, student):
    name = 'Model{0}'.format(model_number)
    if has_logs(student):
        name = name + 'Logs'
    if completed_survey(student):
        name = name + 'Survey'
    return name


def model_subindex(student):
    hasLogs = has_logs(student)
    hasSurvey = completed_survey(student)
    if not hasLogs and not hasSurvey:
        return 0
    elif not hasLogs and hasSurvey:
        return 1
    elif hasLogs and not hasSurvey:
        return 2
    else:
        return 3

def completed_survey(student):
    return student.Age is not None

def has_logs(student):
    return student.AccessCount is not None
