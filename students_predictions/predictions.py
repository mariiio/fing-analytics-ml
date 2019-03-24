# -*- coding: utf-8 -*-
from sklearn import tree
import graphviz
from sklearn import metrics
import pickle
from students_predictions.models import *
import django.utils.timezone as tz

def mapStudent(student, model_number):
  maped_student = [mapAssignment(student.Assignment1), mapAssignment(student.Assignment2)]
  if model_number > 1:
    maped_student = maped_student + [mapTest(student.Test1)]
  if model_number > 2:
    maped_student = maped_student + [mapAssignment(student.Assignment3)]
  if model_number > 3:
    maped_student = maped_student + [mapAssignment(student.Assignment4)]

  if has_logs(student):
    maped_student = maped_student + mapLogs(student)
  if completed_first_survey(student):
    maped_student = maped_student + mapFirstSurvey(student)
  if completed_second_survey(student):
    maped_student = maped_student + mapSecondSurvey(student)

  return maped_student

def mapLogs(student):
  return[mapAccessCount(student.AccessCount),mapForumActivityCount(student.ForumActivityCount),
  mapFileAccessCount(student.FileAccessCount)]

def mapFirstSurvey(student):
  return [mapAge(student.age), mapOrigin(student.location),
  mapEducation(student.education), mapWork(student.works),
  mapWorkRelated(student.works_related), mapCount(student.semester_subjects_count),
  mapReTake(student.course_take_count), mapMotivation(student.motivation_level)]

def mapSecondSurvey(student):
  return [mapAsistance(student.assists_theoretical), mapAsistance(student.assists_practical),
  mapGroup(student.study_method), mapTimeDedicated(student.study_hours)]

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

def mapTest(x):
  if not x or 0 <= int(x) <= 24:
    return 2
  elif 25 <= int(x) <= 59:
    return 1
  return 0

def mapAssignment(x):
  if 0 <= int(x) <= 64:
    return 2
  elif 65 <= int(x) <= 89:
    return 1
  return 0

# DEFINIR RANGOS
def mapAccessCount(x):
  if 0 <= int(x) <= 64:
    return 2
  elif 65 <= int(x) <= 89:
    return 1
  return 0

def mapForumActivityCount(x):
  if 0 <= int(x) <= 64:
    return 2
  elif 65 <= int(x) <= 89:
    return 1
  return 0

def mapFileAccessCount(x):
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
  students = Student.objects.raw('''SELECT grades.Ci as id, grades.Year, student_logs.AccessCount, student_logs.ForumActivityCount, student_logs.SurveyResponseCount,
                                                student_logs.FileAccessCount, s.age, s.location, s.education,s.works,s.works_related,s.semester_subjects_count,s.course_take_count,
                                                s.assists_theoretical, s.assists_practical, s.study_method, s.study_hours, s.motivation_level, grades.Test1, grades.Test2,
                                                grades.Assignment1, grades.Assignment2, grades.Assignment3, grades.Assignment4, grades.Assignment5, grades.Final
                                        FROM
                                        (
                                          SELECT s.Ci, s.Name, c.year as Year,
                                          min(case when t.Name like "%%Primer Parcial%%" then ar.Result else null end) as Test1,
                                          min(case when t.Name like "%%Segundo Parcial%%" then ar.Result else null end) as Test2,
                                          min(case when a.Name like "%%tarea 1%%" then ar.Result else null end) as Assignment1,
                                          min(case when a.Name like "%%tarea 2%%" then ar.Result else null end) as Assignment2,
                                          min(case when a.Name like "%%tarea 3%%" then ar.Result else null end) as Assignment3,
                                          min(case when a.Name like "%%tarea 4%%" then ar.Result else null end) as Assignment4,
                                          min(case when a.Name like "%%tarea 5%%" then ar.Result else null end) as Assignment5,
                                          min(case when f.Name like "%%Nota Final%%" then ar.Result else null end) as Final
                                           FROM
                                            course_details cd inner join
                                            courses c on cd.CourseId = c.Id inner join
                                            activity_results ar on cd.Id = ar.CourseDetailId inner join
                                            students s on cd.StudentId = s.Id
                                            LEFT OUTER JOIN tests t on ar.TestId = t.Id
                                            LEFT OUTER JOIN finals f on ar.FinalId = f.Id
                                            LEFT OUTER JOIN assignments a on ar.AssignmentId = a.Id
                                            GROUP BY S.Ci, S.Name, c.year, cd.CourseId
                                            LIMIT 10000
                                        ) grades
                                        LEFT OUTER JOIN
                                        (
                                          SELECT log_action.Ci, log_action.Year,
                                          max(case when log_action.Action like "%%ACCESS%%" then log_action.count else 0 end) as AccessCount,
                                          max(case when log_action.Action like "%%FORUM_ACTIVITY%%" then log_action.count else 0 end) as ForumActivityCount,
                                          max(case when log_action.Action like "%%SURVEY_RESPONSE%%" then log_action.count else 0 end) as SurveyResponseCount,
                                          max(case when log_action.Action like "%%FILE_ACCESS%%" then log_action.count else 0 end) as FileAccessCount
                                          FROM (
                                            SELECT s.Ci, l.Action, c.Year, count(*) as count
                                              FROM logs l
                                              INNER JOIN course_details cs on l.CourseDetailId = cs.Id
                                              INNER JOIN students s on cs.StudentId = s.Id
                                              INNER JOIN courses c on cs.CourseId = c.Id
                                            GROUP BY action, s.Ci, cs.CourseId
                                            LIMIT 10000
                                          ) log_action
                                          GROUP BY Ci, Year
                                        ) student_logs on grades.Ci = student_logs.Ci and grades.Year = student_logs.Year
                                        LEFT OUTER JOIN
                                        students_surveys s on grades.Ci = s.ci
                                        WHERE grades.Final is not null
                                        ;''')

  for student in students:
    x_train = []
    y_train = []

    for model_number in range(1, 5):
      x_train.append(mapStudent(student, model_number))
      y_train.append(mapFinalResult(student.Final))
      classifier = tree.DecisionTreeClassifier(criterion="entropy")
      model = model_name(model_number, student)
      print "Model " + model
      print "x_train {0}".format(x_train)
      print "y_train {0}".format(y_train)
      save_model(classifier.fit(x_train, y_train), model)
      x_train = []
      y_train = []

def predict():
  students = Student.objects.raw('''SELECT grades.Ci as id, grades.Year, grades.Id as course_detail_id, student_logs.AccessCount, student_logs.ForumActivityCount, student_logs.SurveyResponseCount,
                                                student_logs.FileAccessCount, s.age, s.location, s.education,s.works,s.works_related,s.semester_subjects_count,s.course_take_count,
                                                s.assists_theoretical, s.assists_practical, s.study_method, s.study_hours, s.motivation_level, grades.Test1, grades.Test2,
                                                grades.Assignment1, grades.Assignment2, grades.Assignment3, grades.Assignment4, grades.Assignment5, grades.Final
                                        FROM
                                        (
                                          SELECT s.Ci, s.Name, c.year as Year, cd.Id,
                                          min(case when t.Name like "%%Primer Parcial%%" then ar.Result else null end) as Test1,
                                          min(case when t.Name like "%%Segundo Parcial%%" then ar.Result else null end) as Test2,
                                          min(case when a.Name like "%%tarea 1%%" then ar.Result else null end) as Assignment1,
                                          min(case when a.Name like "%%tarea 2%%" then ar.Result else null end) as Assignment2,
                                          min(case when a.Name like "%%tarea 3%%" then ar.Result else null end) as Assignment3,
                                          min(case when a.Name like "%%tarea 4%%" then ar.Result else null end) as Assignment4,
                                          min(case when a.Name like "%%tarea 5%%" then ar.Result else null end) as Assignment5,
                                          min(case when f.Name like "%%Nota Final%%" then ar.Result else null end) as Final
                                           FROM
                                            course_details cd inner join
                                            courses c on cd.CourseId = c.Id inner join
                                            activity_results ar on cd.Id = ar.CourseDetailId inner join
                                            students s on cd.StudentId = s.Id
                                            LEFT OUTER JOIN tests t on ar.TestId = t.Id
                                            LEFT OUTER JOIN finals f on ar.FinalId = f.Id
                                            LEFT OUTER JOIN assignments a on ar.AssignmentId = a.Id
                                            GROUP BY S.Ci, S.Name, c.year, cd.CourseId, cd.Id
                                            LIMIT 10000
                                        ) grades
                                        LEFT OUTER JOIN
                                        (
                                          SELECT log_action.Ci, log_action.Year,
                                          max(case when log_action.Action like "%%ACCESS%%" then log_action.count else 0 end) as AccessCount,
                                          max(case when log_action.Action like "%%FORUM_ACTIVITY%%" then log_action.count else 0 end) as ForumActivityCount,
                                          max(case when log_action.Action like "%%SURVEY_RESPONSE%%" then log_action.count else 0 end) as SurveyResponseCount,
                                          max(case when log_action.Action like "%%FILE_ACCESS%%" then log_action.count else 0 end) as FileAccessCount
                                          FROM (
                                            SELECT s.Ci, l.Action, c.Year, count(*) as count
                                              FROM logs l
                                              INNER JOIN course_details cs on l.CourseDetailId = cs.Id
                                              INNER JOIN students s on cs.StudentId = s.Id
                                              INNER JOIN courses c on cs.CourseId = c.Id
                                            GROUP BY action, s.Ci, cs.CourseId
                                            LIMIT 10000
                                          ) log_action
                                          GROUP BY Ci, Year
                                        ) student_logs on grades.Ci = student_logs.Ci and grades.Year = student_logs.Year
                                        LEFT OUTER JOIN
                                        students_surveys s on grades.Ci = s.ci
                                        WHERE grades.Final is null
                                        ;''')

  for student in students:
    number = model_number(student)
    model = model_name(number, student)
    prediction = {2: 'Recursa', 1: 'Derecho a examen', 0: 'Exonera'}[retrieve_model(model).predict([mapStudent(student, number)])]
    Prediction(CourseDetailId = student.course_detail_id, Result = prediction, Timestamp = tz.localtime()).save()

def save_model(classifier, model_name):
  file = open(model_name, 'w')
  pickle.dump(classifier, file)
  file.close()

def retrieve_model(model_name):
  file = open(model_name, 'r')
  return pickle.load(file)

def model_number(student):
  if student.Assignment4:
    return 4
  elif student.Assignment3:
    return 3
  elif Test1:
    return 2
  else:
    return 1

def model_name(model_number, student):
  name = 'Model{0}'.format(model_number)
  if has_logs(student):
    name = name + 'Logs'
  if completed_first_survey(student):
    name = name + 'FirstSurvey'
  if completed_second_survey(student):
    name = name + 'SecondSurvey'
  return name

def completed_first_survey(student):
  return student.age is not None

def completed_second_survey(student):
  return student.assists_theoretical is not None

def has_logs(student):
  return student.AccessCount is not None
