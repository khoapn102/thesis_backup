from openerp import models, fields, api

class Major(models.Model):
    
    _inherit = 'major'
    
    # Academic Program
    std_academic_prog_id = fields.Many2one('student.academic.program', 
                                           string='Academic Program')
    
    # Curriculum
    
    