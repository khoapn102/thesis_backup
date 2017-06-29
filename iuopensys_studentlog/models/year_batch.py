from openerp import models, fields, api

class YearBatch(models.Model):
    
#     def _get_default_all_students(self):
#         cr = self.pool.cursor()
#         return self.pool.get('student').search(cr,self.env.uid,[('graduation_status','in',['ontrack','ie','complete','readygrad'])])
#     student_list = fields.Many2many('student', string='All Students',
#                                     default=_get_default_all_students)
   
    _inherit='year.batch'
    
    student_ids = fields.One2many('student', 'year_batch_id', string='Intake Students')
    number_intake_students = fields.Integer(string='Students', compute='get_new_students_details')
    
    number_students_ready_graduate = fields.Integer(string='Students')

    graduate_student_ids = fields.Many2many('student',string='Graduating Students',
                                              help='Students who are ready to graduate this year.')
    

    # Button Print Graduating Students
    @api.multi
    def print_graduating_student_list(self):
        report_name = 'iuopensys_studentlog.report_graduating_student'
        return self.env['report'].get_action(self, report_name)
    
    @api.multi
    def update_graduating_student(self):
        for record in self:
            # Get all ready to grad student with intake year less than or equal to the current year_batch record
            # Only get student who ontrack/ready -> to easy check if UI not updated
            student_ids = self.env['student'].search([('year_batch_id.year', '<', record.year),
                                                      ('graduation_status','in',['ontrack','complete','readygrad'])])
            res_ids = student_ids.ids
            for student in student_ids:
                if (student.major_incomplete_credits == 0 and student.major_total_credits > 0)\
                    or student.graduation_status in ['complete','readygrad']:
                    continue
                else:
                    res_ids.remove(student.id)
            # Remove all the ontrack student
#             if len(res_ids) < len(student_ids.ids):
            student_ids = self.env['student'].search([('id','in',res_ids)])
            record.graduate_student_ids = student_ids
            record.number_students_ready_graduate = len(student_ids.ids)
                    
                                
#     @api.depends('student_list')
#     def get_year_report_for_all_students(self):
#         for record in self:
#             res_ids = self.env['student'].search([('graduation_status','in',['complete','readygrad'])])
#             record.graduating_student_ids = res_ids
    
    @api.depends('student_ids')
    def get_new_students_details(self):
        for record in self:
            record.number_intake_students = len(record.student_ids.ids)
            
    @api.multi
    def name_get(self):
        res = super(YearBatch,self).name_get()
        data = []
        for record in self:
            val = ''
            val += record.name or ''
            val += ' (' + record.year_code + ')'
            data.append((record.id, val))
        return data
        
        
        
        