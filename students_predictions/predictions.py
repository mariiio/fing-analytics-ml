# -*- coding: utf-8 -*-
from sklearn import tree
import graphviz
from sklearn import metrics
import pickle
from students_predictions.models import StudentSurvey, CourseResult

# SURVEYS

def mapSurvey(student):
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

def train_survey_model():
  x_train = []
  y_train = []
  trainData = StudentSurvey.objects.all()

  for student in trainData:
      x_train.append(mapSurvey(student))
      y_train.append(mapResult(student.result))

  classifier = tree.DecisionTreeClassifier(criterion="entropy", max_depth=10)
  save_survey_model(classifier.fit(x_train, y_train))

def predict_student_survey(ci):
  student = StudentSurvey.objects.get(ci=ci)
  return retrieve_survey_model().predict([mapSurvey(student)])

def save_survey_model(classifier):
  file = open('storedSurveyModel', 'w')
  pickle.dump(classifier, file)
  file.close()

def retrieve_survey_model():
  file = open('storedSurveyModel', 'r')
  return pickle.load(file)

# COURSE RESULTS

def mapCourse(student):
    return [mapTest(student.test1), mapTest(student.test2),
    mapAssignment(student.assignment1), mapAssignment(student.assignment2),
    mapAssignment(student.assignment3), mapAssignment(student.assignment4),
    mapAssignment(student.assignment5)]

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

def train_course_model():
  x_train = []
  y_train = []
  trainData = CourseResult.objects.raw('''SELECT d1.Ci as id, d1.Year, d1.AccessCount, d1.ForumActivityCount, d1.SurveyResponseCount,
                                                d1.FileAccessCount, d2.Test1, d2.Test2, d2.Assignment1, d2.Assignment2,
                                                d2.Assignment3, d2.Assignment4, d2.Assignment5, d2.Final
                                          FROM
                                            (SELECT d.Ci, d.Year,
                                              max(case when d.Action like "%%ACCESS%%" then d.count else 0 end) as AccessCount,
                                              max(case when d.Action like "%%FORUM_ACTIVITY%%" then d.count else 0 end) as ForumActivityCount,
                                              max(case when d.Action like "%%SURVEY_RESPONSE%%" then d.count else 0 end) as SurveyResponseCount,
                                              max(case when d.Action like "%%FILE_ACCESS%%" then d.count else 0 end) as FileAccessCount
                                            FROM (
                                              SELECT s.Ci, l.Action, c.Year, count(*) as count
                                                FROM logs l
                                                INNER JOIN course_details cs on l.CourseDetailId = cs.Id
                                                INNER JOIN students s on cs.StudentId = s.Id
                                                INNER JOIN courses c on cs.CourseId = c.Id
                                              WHERE cs.CourseId = 1
                                              GROUP BY action, s.Ci
                                            ) d
                                          GROUP BY Ci, Year) d1
                                          JOIN
                                            (SELECT s.Ci, s.Name, c.year as Year,
                                              min(case when t.Name like "%%Primer Parcial%%" then ar.Result else null end) as Test1,
                                              min(case when t.Name like "%%Segundo Parcial%%" then ar.Result else null end) as Test2,
                                              min(case when a.Name like "%%tarea 1%%" then ar.Result else null end) as Assignment1,
                                              min(case when a.Name like "%%tarea 2%%" then ar.Result else null end) as Assignment2,
                                              min(case when a.Name like "%%tarea 3%%" then ar.Result else null end) as Assignment3,
                                              min(case when a.Name like "%%tarea 4%%" then ar.Result else null end) as Assignment4,
                                              min(case when a.Name like "%%tarea 5%%" then ar.Result else null end) as Assignment5,
                                              min(case when f.Name like "%%Curso%%" then ar.Result else null end) as Final
                                             FROM
                                              course_details cd inner join
                                                courses c ON cd.CourseId = c.Id INNER JOIN
                                                activity_results ar ON cd.Id = ar.CourseDetailId INNER JOIN
                                                students s ON cd.StudentId = s.Id
                                                LEFT OUTER JOIN tests t on ar.TestId = t.Id
                                                LEFT OUTER JOIN finals f on ar.FinalId = f.Id
                                                LEFT OUTER JOIN assignments a on ar.AssignmentId = a.Id
                                            where cd.CourseId = 1
                                              GROUP BY S.Ci, S.Name, c.year
                                            ) d2
                                          ON d1.Ci = d2.Ci AND d1.Year = d2.Year;''')

  for course_result in trainData:
      x_train.append(mapCourse(course_result))
      y_train.append(mapFinalResult(course_result.final))

  classifier = tree.DecisionTreeClassifier(criterion="entropy", max_depth=10)
  save_course_model(classifier.fit(x_train, y_train))

def predict_student_course(ci):
  student = CourseResult.objects.get(ci=ci)
  return retrieve_course_model().predict([mapCourse(student)])

def save_course_model(classifier):
  file = open('storedCourseModel', 'w')
  pickle.dump(classifier, file)
  file.close()

def retrieve_course_model():
  file = open('storedCourseModel', 'r')
  return pickle.load(file)
