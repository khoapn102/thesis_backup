from openerp import models, fields, api

class StudentCourse(models.Model):
    
    _name = 'student.course'
    _description = 'Registered Course of Student'
    
    offer_course_id = fields.Many2one('offer.course', string='Offer Course')
    student_id = fields.Many2one('student', string='Student')
    
    studentId = fields.Char(string='Student ID', related='student_id.studentId')
    student_lname = fields.Char(string='Last Name', related='student_id.last_name')
    student_fname = fields.Char(string='First Name', related='student_id.name')
    student_class_code = fields.Char(string='Student Class Code', related='student_id.student_class_code')
    
    course_code = fields.Char(string='Course Code', related='offer_course_id.course_code')
    course_name = fields.Char(string='Course Name', related='offer_course_id.name')
    
    mid_score = fields.Float(string='Midterm Exam Score', default=0.0)
    final_score = fields.Float(string='Final Exam Score', default=0.0)
    
    course_gpa = fields.Float(string='Course GPA', compute='_compute_course_gpa')
    
    @api.multi
    def _compute_course_gpa(self):
        for record in self:
            mid_avg = record.mid_score * record.offer_course_id.mid_exam_percent
            fin_avg = record.final_score * record.offer_course_id.final_exam_percent
            record.course_gpa = (mid_avg + fin_avg)/100
    
    
    