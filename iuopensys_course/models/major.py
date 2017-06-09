from openerp import models, fields, api

class Major(models.Model):
    
    _inherit = 'major'
    
    # Academic Program
    std_academic_prog_id = fields.Many2one('student.academic.program', 
                                           string='Academic Program')
    
    # Curriculum
    iu_curriculum_ids = fields.Many2many('iu.curriculum', string='List of curriculums')
    course_ids = fields.Many2many('course', string='List of Course', compute='get_all_course_ids')
    
    # Total Credits
    major_total_credits = fields.Integer(string='Total Req. Credits', compute='get_all_course_ids',
                                         help='Total Required Credits for Graduation')
    major_total_not_count_credits = fields.Integer(string='Total P/F Credits',
                                                   compute='get_all_course_ids') 
    major_total_with_no_count_credits = fields.Integer(string='Total Credits (incl. P/F)',
                                                       compute='get_all_course_ids')
#     @api.onchange('iu_curriculum_ids')
#     def onchange_iu_curriculum(self):
#         if self.iu_curriculum_ids:
#             ids_res = []
#             for curriculum in self.iu_curriculum_ids:
#                 if curriculum.course_ids:
#                     for course in curriculum.course_ids:
#                         ids_res.append(course.id)
#             
#             self.course_ids = ids_res
         
    @api.depends('iu_curriculum_ids')
    def get_all_course_ids(self):
        for record in self:
            if record.iu_curriculum_ids:
                total_cred = 0
                ids_res = []
                total_cred_no_count = 0
                for curriculum in record.iu_curriculum_ids:
                    if curriculum.course_ids:
                        for course in curriculum.course_ids:
                            ids_res.append(course.id)
                    # IE Curriculum will be ignored. Only added For registration
                    if curriculum.is_eng_req:
                        continue
                    total_cred += curriculum.max_cred_require
                    total_cred_no_count += curriculum.total_cred_not_count
                record.course_ids = ids_res
                record.major_total_credits = total_cred
                record.major_total_not_count_credits = total_cred_no_count
                record.major_total_with_no_count_credits = total_cred + total_cred_no_count
            
    @api.onchange('std_academic_prog_id')
    def onchange_std_academic_prog(self):
        if self.std_academic_prog_id:
            if self.name:
                self.name = self.name.split('-')[0] + ' - ' +\
                            self.std_academic_prog_id.program_code
            else:
                self.name = ' - ' + self.std_academic_prog_id.program_code