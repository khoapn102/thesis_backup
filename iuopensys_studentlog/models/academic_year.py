from openerp import models,fields,api

class AcademicYear(models.Model):
    
    _inherit = 'academic.year'
    
    student_ids = fields.One2many('student', 'academic_year_id', string='Intake Students')
    