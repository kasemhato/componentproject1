#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import users
from webapp2_extras import sessions
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
import os
from google.appengine.ext.webapp import template
from classesAndInit import *

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class HomeHandler(BaseHandler):
    def get(self):
        init()
        file = os.path.join(os.path.dirname(__file__), 'logInPage.html')

        self.response.out.write(template.render(file, None))

    def post(self):
        if(self.session.get('name') != None):
            del(self.session['name'])

        file = os.path.join(os.path.dirname(__file__), 'logInPage.html')

        self.response.out.write(template.render(file, None))

class RegisterStudent(BaseHandler):
    def get(self):
        file = os.path.join(os.path.dirname(__file__), 'registerStudent.html')

        self.response.out.write(template.render(file, None))

class StudentAdded(BaseHandler):
    def post(self):
        name = self.request.get('name')
        password = self.request.get('password')
        phone = self.request.get('phone')
        email = self.request.get('email')
        major = self.request.get('major')
        ID = self.request.get('ID')

        s = Student()
        s.name = name
        s.password = password
        s.phone = phone
        s.email = email
        s.major = major
        s.ID = ID
        s.creditscount = 0
        s.isAdmin = False
        s.put()

        context = {
            'student': s
        }
        file = os.path.join(os.path.dirname(__file__), 'studentAdded.html')
        self.response.out.write(template.render(file, context))

class logInFeedback(BaseHandler):
    def post(self):
        q = db.Query(Student).filter('name =', self.request.get('username'))
        password = self.request.get('password')
        s = Student()
        s = q.get()

        if s != None and s.password == password:
            self.session['name'] = s.name           #"{studentId:'1'}"
            self.session['ID'] = s.ID
            self.session['phone'] = s.phone
            self.session['email'] = s.email
            self.session['major'] = s.major
            self.session['creditscount'] = s.creditscount
            self.session['passed'] = s.passed

            context = {
                'isAdmin': s.isAdmin,
                'name': self.session.get('name')
            }
            file = os.path.join(os.path.dirname(__file__), 'logInFeedback.html')
            self.response.out.write(template.render(file, context))
        else:
            self.redirect('/')

class viewSchedulePage(BaseHandler):
    def get(self):
        s = db.Query(Student).filter('ID =', self.session.get('ID')).get()
        sq = db.Query(Registration).filter('student =', s.key()) #get the subjects that this student takes
        context = {
            'subjects': sq,
            'name': self.session.get('name'),
            'student': s
        }
        file = os.path.join(os.path.dirname(__file__), 'viewSchedule.html')
        self.response.write("can't register more than 21 credit hours")
        self.response.out.write(template.render(file, context))

    def post(self):
        s = db.Query(Student).filter('ID =', self.session.get('ID')).get()
        sq = db.Query(Registration).filter('student =', s.key()) #get the subjects that this student takes
        context = {
            'subjects': sq,
            'name': self.session.get('name'),
            'student': s
        }
        file = os.path.join(os.path.dirname(__file__), 'viewSchedule.html')

        self.response.out.write(template.render(file, context))

class addSubjectPage(BaseHandler):
    def post(self):
        q = db.Query(Course)
        student = db.Query(Student).filter('ID =', self.session.get('ID')).get()
        qr = db.Query(Registration).filter('student =',student.getKey())
        if student.creditscount < 22 :
            myList = list()
            for course in q:
                flag = 0
                for entry in qr:
                    if entry.course.key() == course.key():
                        flag = 1

                if flag == 0:
                    myList.append(course)

            context ={
                'subjects' : myList,
                'registeration' : qr
            }
            file = os.path.join(os.path.dirname(__file__), 'addSubject.html')

            self.response.out.write(template.render(file, context))
        else:
            self.redirect("/viewSchedule")

class subjectAddedPage(BaseHandler):
    def post(self):
        name = self.request.get('subject')
        subject = Course.get(name)
        student = db.Query(Student).filter('ID =', self.session.get('ID')).get()
        qr = db.Query(Registration).filter('student =', student.getKey())
        flag = 1
        if student.creditscount + subject.credits < 22:
            for entry in qr:
                if entry.course.time == subject.time and entry.course.days == subject.days:
                    flag = 0
            if flag:
                student.creditscount += subject.credits
                self.session['creditscount'] = student.creditscount + subject.credits
                student.put()

                register = Registration()
                register.course = subject
                register.student = student
                register.put()
                html = "Subject registered successfully"
            else:
                html = "You have a conflict"

        else:
            html = "Can't register more than 21 credit hours"


        context ={
                'html': html,
                'subject' : subject
            }
        file = os.path.join(os.path.dirname(__file__), 'subjectAdded.html')

        self.response.out.write(template.render(file, context))

class subjectDeletedPage(BaseHandler):
    def post(self):
        student = db.Query(Student).filter('ID =', self.session.get('ID')).get()
        key = self.request.get('subject')
        subject = Registration.get(key)
        name = subject.course.name
        if subject.course.name:
            student.creditscount -= subject.course.credits
            self.session['creditscount'] = student.creditscount - subject.course.credits
            student.put()
            subject.delete()

            context ={
                'name' : name
            }
            file = os.path.join(os.path.dirname(__file__), 'subjectDeleted.html')

            self.response.out.write(template.render(file, context))
        else:
            self.redirect('/viewSchedule')

class viewStudentPage(BaseHandler):
    def post(self):
        context = {
            'name': self.session.get('name'),
            'phone': self.session.get('phone'),
            'email': self.session.get('email'),
            'major': self.session.get('major'),
            'ID': self.session.get('ID')
        }
        file = os.path.join(os.path.dirname(__file__), 'viewStudent.html')

        self.response.out.write(template.render(file, context))

class editStudentPage(BaseHandler):
    def post(self):
        context = {
            'name': self.session.get('name'),
            'phone': self.session.get('phone'),
            'email': self.session.get('email'),
            'major': self.session.get('major'),
            'ID': self.session.get('ID')
        }
        file = os.path.join(os.path.dirname(__file__), 'editStudent.html')

        self.response.out.write(template.render(file, context))

class StudentEdited(BaseHandler):
    def post(self):
        name = self.request.get('name')
        password = self.request.get('password')
        phone = self.request.get('phone')
        email = self.request.get('email')
        major = self.request.get('major')
        ID = self.request.get('ID')

        student = db.Query(Student).filter('ID =', self.session.get('ID')).get()   #edit student info
        student.name = name
        if self.request.get('password') != "":
            student.password = password
        student.phone = phone
        student.email = email
        student.major = major
        student.ID = ID
        student.put()

        self.session['name'] = student.name           #edit the session info
        self.session['ID'] = student.ID
        self.session['phone'] = student.phone
        self.session['email'] = student.email
        self.session['major'] = student.major

        context = {
            'student': student
        }
        file = os.path.join(os.path.dirname(__file__), 'studentEdited.html')
        self.response.out.write(template.render(file, context))

class adminPage(BaseHandler):
    def get(self):

        file = os.path.join(os.path.dirname(__file__), 'adminPage.html')
        context = {
            'name' : self.session.get('name')
        }
        self.response.out.write(template.render(file, context))

    def post(self):

        file = os.path.join(os.path.dirname(__file__), 'adminPage.html')
        context = {
            'name' : self.session.get('name')
        }
        self.response.out.write(template.render(file, context))

class viewCourseAdmin(BaseHandler):
    def post(self):
        course = db.Query(Course).filter('code =', self.request.get('courseID')).get()
        if course != None :
            students = db.Query(Registration).filter('course =', course.getKey())
            context = {
                'students' : students,
                'course' : course
            }
            file = os.path.join(os.path.dirname(__file__), 'viewCourseAdmin.html')
            self.response.out.write(template.render(file, context))
        else:
            self.redirect("/adminPage")

class viewStudentAdmin(BaseHandler):
    def post(self):
        student = db.Query(Student).filter('ID =', self.request.get('studentID')).get()
        if student != None :
            courses = db.Query(Registration).filter('student =', student.getKey())
            context = {
                'courses' : courses,
                'student' : student
            }
            file = os.path.join(os.path.dirname(__file__), 'viewStudentAdmin.html')
            self.response.out.write(template.render(file, context))
        else:
            self.redirect("/adminPage")


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
                               ('/', HomeHandler), \
                               ('/registerStudent', RegisterStudent), \
                               ('/studentAdded', StudentAdded), \
                               ('/logInFeedback', logInFeedback), \
                               ('/viewSchedule', viewSchedulePage), \
                               ('/addSubject', addSubjectPage), \
                               ('/subjectAdded', subjectAddedPage), \
                               ('/subjectDeleted', subjectDeletedPage), \
                               ('/viewStudent', viewStudentPage), \
                               ('/editStudent', editStudentPage), \
                               ('/studentEdited', StudentEdited), \
                               ('/adminPage', adminPage), \
                               ('/viewCourseAdmin', viewCourseAdmin), \
                               ('/viewStudentAdmin', viewStudentAdmin)],
                              config=config, debug=True)
