from openerp import models, fields, api

class IuCurriculum(models.Model):
    
    _name = 'iu.curriculum'
    _description = 'Curriculum at IU'
    
    name = fields.Char(string='Name')
    department_id = fields.Many2one('department', string='Department')
    max_cred_require = fields.Integer('Max Credits Requires')
    total_cred = fields.Integer('Total Credits', compute='get_total_cred')
    is_eng_req = fields.Boolean('Intensive English')
    note = fields.Text('Note')
    
    # List of course
    course_ids = fields.Many2many('course', string='Course List')
    
    @api.depends('course_ids')
    def get_total_cred(self):
        for record in self:
            if record.course_ids:
                total = 0
                for course in record.course_ids:
                    total += course.number_credits
                record.total_cred = total
