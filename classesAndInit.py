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

from google.appengine.ext import db


class Course(db.Model):
    name = db.StringProperty()
    instructor = db.StringProperty()
    time = db.StringProperty()
    days = db.StringProperty()
    code = db.StringProperty()

    def getKey(self):
        return self.key()


class Student(db.Model):
    name = db.StringProperty()
    password = db.StringProperty()
    phone = db.PhoneNumberProperty()
    email = db.EmailProperty()
    major = db.StringProperty()
    ID = db.StringProperty()
    isAdmin = db.BooleanProperty()

    def getKey(self):
        return self.key()

class Registration(db.Model):
    student = db.ReferenceProperty(Student)
    course = db.ReferenceProperty(Course)

    def getKey(self):
        return self.key()


def init():
    s = Student.get_or_insert('s')
    if s.name:
        pass
    else:
        s.name = "Qasem Hato"
        s.password = "1234"
        s.phone = "0798414533"
        s.email = "q.elhato@gju.edu.jo"
        s.major = "CS"
        s.ID = "20131501035"
        s.isAdmin = True
        s.put()

    c = Course.get_or_insert('c')
    if c.name:
        pass
    else:
        c.name = "Component Based Computing"
        c.instructor = "Dr. Isamil Hababeh"
        c.time = "09:30"
        c.days = "SUN/TUE"
        c.code = "CS311"
        c.put()

    c = Course.get_or_insert('alg')
    if c.name:
        pass
    else:
        c.name = "Algorithms And Data Structure"
        c.instructor = "Dr. Cristina Class"
        c.time = "09:30"
        c.days = "MON/WED"
        c.code = "CS211"
        c.put()

    r = Registration.get_or_insert('r')
    if r.student:
        pass
    else:
        r.student = s
        r.course = c
        r.put()
