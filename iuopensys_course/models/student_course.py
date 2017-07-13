from openerp import models, fields, api

class StudentCourse(models.Model):
    
    _name = 'student.course'
    _description = 'Registered Course of Student'   
    
    name = fields.Char(string='Name', default='Student Course Transcript')
    
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
    course_type = fields.Selection(string='Type', related='offer_course_id.course_type')
    crs_lang = fields.Selection(string='Language', related='offer_course_id.crs_lang')
    department_id = fields.Many2one(string='Department', related='offer_course_id.department_id')  
    semester_id = fields.Many2one(related='offer_course_id.semester_id',
                                  store=True)
    prereq_course_id = fields.Many2one(related='offer_course_id.course_id.prereq_course_id')
    
    # Course Examination Info
    has_exam = fields.Boolean(related='offer_course_id.has_exam')
    display_exam_date_midterm = fields.Text(related='offer_course_id.display_exam_date_midterm')
    display_exam_time_midterm = fields.Text(related='offer_course_id.display_exam_time_midterm')
    display_duration_midterm = fields.Text(related='offer_course_id.display_duration_midterm')
    display_room_midterm = fields.Text(related='offer_course_id.display_room_midterm')
    display_exam_date_final = fields.Text(related='offer_course_id.display_exam_date_final')
    display_exam_time_final = fields.Text(related='offer_course_id.display_exam_time_final')
    display_duration_final = fields.Text(related='offer_course_id.display_duration_final')
    display_room_final = fields.Text(related='offer_course_id.display_room_final')
    
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
    amount_session = fields.Integer(related='offer_course_id.amount_session')
    s1 = fields.Boolean('s1')
    s2 = fields.Boolean('s2')    
    s3 = fields.Boolean('s3')
    s4 = fields.Boolean('s4')
    s5 = fields.Boolean('s5')
    s6 = fields.Boolean('s6')
    s7 = fields.Boolean('s7')
    s8 = fields.Boolean('s8')
    s9 = fields.Boolean('s9')
    s10 = fields.Boolean('s10')
    s11 = fields.Boolean('s11')
    s12 = fields.Boolean('s12')
    s13 = fields.Boolean('s13')
    s14 = fields.Boolean('s14')
    s15 = fields.Boolean('s15')
    s16 = fields.Boolean('s16') 
    
    # Course status per student
    is_complete = fields.Boolean('Completed')
     
    
    @api.multi
    @api.depends('final_score','mid_score','assignment_score')
    def _compute_course_gpa(self):
        for record in self:
            if record.final_score >= 0 and record.offer_course_id.final_exam_percent:
                mid_avg = record.mid_score * record.offer_course_id.mid_exam_percent
                fin_avg = record.final_score * record.offer_course_id.final_exam_percent
                assign_avg = record.assignment_score * record.offer_course_id.assignment_percent
                record.course_gpa = round(mid_avg + fin_avg + assign_avg)
                
                classify = {'A+':(90.0, 100.0),
                            'A':(80.0, 89.0),
                            'B+':(70.0, 79.0),
                            'B':(60.0, 69.0),
                            'C':(52.0, 59.0),
                            'D':(50.0,51.0),
                            'F':(0, 49.0)}
                for item in classify:
                    if classify[item][0] <= record.course_gpa <= classify[item][1]:
                        record.letter_grade = item
                        break
                    
#                 passing_grade = self.env['ir.config_parameter'].get_param('iuopensys_course.course_passing_grade')
#                 if record.course_gpa >= float(passing_grade):
#                     if record.is_complete == False:
#                         record.write({'is_complete': True})
#                 else:
#                     if record.is_complete:
#                         record.write({'is_complete': False})
    
    # No write() functions because for simplify purpose. Student.course can only
    # be created/deleted
    
    # Onchagne final_score -> will check if is completed or not.
    @api.onchange('final_score','mid_score', 'assignment_score')
    def onchange_final_score(self):
        if self.final_score or self.mid_score or self.assignment_score:
            passing_grade = self.env['ir.config_parameter'].get_param('iuopensys_course.course_passing_grade')
            if self.course_gpa >= float(passing_grade):
#                 print '======== HERE'
                if not self.is_complete:
                    self.is_complete = True
            else:
                self.is_complete = False
            
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
#                             print '======Event Partner =====', event.partner_ids
        return models.Model.unlink(self)
    
    