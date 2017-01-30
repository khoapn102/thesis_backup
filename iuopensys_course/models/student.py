from openerp import models, fields, api

class Student(models.Model):
    
    _inherit = 'student'
    
    # Course list referenced to student
    student_course_ids = fields.One2many('student.course', 'student_id',
                                         string='Courses')