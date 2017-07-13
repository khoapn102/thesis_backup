from openerp import models, fields, api

class StudentExaminationSchedule(models.Model):
    
    _name = 'student.examination.schedule'
    _description = 'Display Examination Schedule for Student'
    
    name = fields.Char('Name', default='Examination Schedule')
    student_id = fields.Many2one('student', string='Student')
    semester_id = fields.Many2one('semester', string='Semester')
    exam_status = fields.Boolean(related='student_id.exam_status')
    
    exam_type = fields.Selection(selection=[('mid','Midterm'),
                                            ('final','Final')],
                                 string='Exam Type')
    
    student_course_midterm_ids = fields.Many2many('student.course', string='Exam List', compute='get_course_schedule')
    student_course_final_ids = fields.Many2many('student.course', string='Exam List', compute='get_course_schedule')
    
    @api.depends('student_id', 'semester_id', 'exam_type')
    def get_course_schedule(self):
        for record in self:
            if record.student_id and record.semester_id and record.exam_type:
                std_crs_ids = self.env['student.course'].search([('student_id','=',record.student_id.id),
                                                                 ('semester_id','=',record.semester_id.id),
                                                                 ('has_exam','=',True)])
                if std_crs_ids:
                    record.student_course_midterm_ids = std_crs_ids
                    record.student_course_final_ids = std_crs_ids
    