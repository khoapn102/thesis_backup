from openerp import models, fields, api

class StudentCourse(models.Model):
    
    _name = 'student.course'
    _description = 'Registered Course of Student'   
    
    
    # Student
    student_id = fields.Many2one('student', string='Student', ondelete="cascade")    
    studentId = fields.Char(string='Student ID', related='student_id.studentId')
    student_lname = fields.Char(string='Last Name', related='student_id.last_name')
    student_fname = fields.Char(string='First Name', related='student_id.name')
    student_class_code = fields.Char(string='Student Class Code', related='student_id.student_class_code')
    
    # Course
    offer_course_id = fields.Many2one('offer.course', string='Offer Course', ondelete="cascade")
    course_code = fields.Char(string='Course Code', related='offer_course_id.course_code')
    course_name = fields.Char(string='Course Name', related='offer_course_id.name')
    course_credits = fields.Integer(string='Credits', related='offer_course_id.course_id.number_credits')    
    semester_id = fields.Many2one(related='offer_course_id.semester_id')
    
    # GPA
    mid_exam_percent = fields.Float(string="Mid %", related="offer_course_id.mid_exam_percent")
    final_exam_percent = fields.Float(string="Final %", related="offer_course_id.final_exam_percent")
    assignment_percent = fields.Float(string="Assign. %", related="offer_course_id.assignment_percent")
      
    mid_score = fields.Float(string='Midterm Exam Score', default=0.0)
    final_score = fields.Float(string='Final Exam Score', default=0.0)
    assignment_score = fields.Float(string='Assignment Score', default=0.0)
    
    course_gpa = fields.Float(string='Course GPA', compute='_compute_course_gpa')
    letter_grade = fields.Char(string='Letter Grade', compute='_compute_course_gpa')
    classification = fields.Char(string='Classification', compute='_compute_course_gpa')
    ext_note = fields.Char(string='Note')
    
    # Exam status (eligible to take test or not)
    exam_status = fields.Boolean(string='Eligible for Exam',
                                 related='student_id.exam_status')
    
    # Attendance
    
    
    @api.multi
    def _compute_course_gpa(self):
        for record in self:
            if record.final_score:
                mid_avg = record.mid_score * record.offer_course_id.mid_exam_percent
                fin_avg = record.final_score * record.offer_course_id.final_exam_percent
                assign_avg = record.assignment_score * record.offer_course_id.assignment_percent
                record.course_gpa = mid_avg + fin_avg + assign_avg
                
                classify = {'A+':(90, 100),
                            'A':(80, 89),
                            'B+':(70, 79),
                            'B':(60, 69),
                            'C':(52, 59),
                            'D':(50,51),
                            'F':(0, 49)}
                for item in classify:
                    if classify[item][0] <= record.course_gpa <= classify[item][1]:
                        record.letter_grade = item
                        break
    
    # No write() functions because for simplify purpose. Student.course can only
    # be created/deleted
            
    @api.model
    def create(self, vals):
        curr_rec = super(StudentCourse,self).create(vals)
        if curr_rec.offer_course_id.study_session_ids:
            for session in curr_rec.offer_course_id.study_session_ids:
                event_ids = self.env['calendar.event'].search([('offer_course_id','=',curr_rec.offer_course_id.id),
                                                                                   ('study_period_id', '=', session.id)],
                                                                                  order='id asc', limit=1)
#                 print '++++++++++', event_ids
                if event_ids:
                    event_vals = {}
                    for event in event_ids:
                        event['partner_ids'] = [(4, curr_rec.student_id.user_id.partner_id.id)]
        return curr_rec
    
    @api.multi
    def unlink(self):
        for record in self:
            if record.offer_course_id.study_session_ids:
                for session in record.offer_course_id.study_session_ids:
                    event_ids = self.env['calendar.event'].search([('offer_course_id','=',record.offer_course_id.id),
                                                                                   ('study_period_id', '=', session.id)],
                                                                                  order='id asc', limit=1)
#                     print '======', event_ids
                    if event_ids:
                        for event in event_ids:
                            event.partner_ids = [(3, record.student_id.user_id.partner_id.id)]
                            print '======Event Partner =====', event.partner_ids
        return models.Model.unlink(self)
    
    