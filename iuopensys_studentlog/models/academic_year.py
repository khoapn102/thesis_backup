from openerp import models,fields,api

class AcademicYear(models.Model):
    
    _inherit = 'academic.year'
    
    student_ids = fields.One2many('student', 'academic_year_id', string='Intake Students')
    user_ids = fields.Many2many('res.users', string='List of Users',
                                compute='get_all_users_in_academic_year',
                                store=True)
    
    @api.depends('student_ids')
    def get_all_users_in_academic_year(self):
        for record in self:
            if record.student_ids:
                user_ids = []
                for student in record.student_ids:
                    user_ids.append(student.user_id.id)
                record.user_ids = user_ids
    