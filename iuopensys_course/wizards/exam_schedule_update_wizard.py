from openerp import models, fields, api

class ExamScheduleUpdateWizard(models.TransientModel):
    
    _name = 'exam.schedule.update.wizard'
    _description = 'Update Schedule Wizard'
    
    semester_id = fields.Many2one('semester', string='Semester',)
    exam_type = fields.Selection(selection=[('mid','Midterm'),
                                            ('final','Final')],
                                 string='Exam Type',
                                 )
    student_ids = fields.Many2many('student', string='Student List', compute='get_all_students')
    
    @api.depends('semester_id')
    def get_all_students(self):
        for record in self:
            if record.semester_id:
                student_res = []
                # Find all courses in Semester that has the EXAM schedule
                offer_course_ids = self.env['offer.course'].search([('semester_id','=',record.semester_id.id),
                                                                ('has_exam','=',True)])
                for course in offer_course_ids:
                    # Get all student in the offering course
                    if course.student_course_ids:
                        for std_crs in course.student_course_ids:
                            if std_crs.student_id.id not in student_res:
                                student_res.append(std_crs.student_id.id)
                                
                record.student_ids = student_res
    
    @api.multi
    def update_schedule(self):
        for record in self:
            if record.student_ids:
                for student in record.student_ids:
                    std_exam_id = self.env['student.examination.schedule'].search([('student_id','=',student.id),
                                                                                   ('semester_id','=',record.semester_id.id),
                                                                                   ('exam_type','=',record.exam_type)])
                    if not std_exam_id:
                        new_vals = {'student_id':student.id,
                                    'semester_id':record.semester_id.id,
                                    'exam_type':record.exam_type}
                        std_exam = self.env['student.examination.schedule']
                        std_exam.create(new_vals)
                        