from openerp import models, fields, api

class Major(models.Model):
    
    _inherit = 'major'
    
    # Academic Program
    std_academic_prog_id = fields.Many2one('student.academic.program', 
                                           string='Academic Program')
    
    # Curriculum
    iu_curriculum_ids = fields.Many2many('iu.curriculum', string='List of curriculums')
    course_ids = fields.Many2many('course', string='List of Course')
        
    @api.onchange('iu_curriculum_ids')
    def onchange_iu_curriculum(self):
        if self.iu_curriculum_ids:
            ids_res = []
            for curriculum in self.iu_curriculum_ids:
                if curriculum.course_ids:
                    for course in curriculum.course_ids:
                        ids_res.append(course.id)
            
            self.course_ids = ids_res
            
    @api.onchange('std_academic_prog_id')
    def onchange_std_academic_prog(self):
        if self.std_academic_prog_id:
            if self.name:
                self.name = self.name.split('-')[0] + ' - ' +\
                            self.std_academic_prog_id.program_code
            else:
                self.name = ' - ' + self.std_academic_prog_id.program_code