from openerp import models, fields, api

class IuCurriculum(models.Model):
    
    _name = 'iu.curriculum'
    _description = 'Curriculum at IU'
    
    name = fields.Char(string='Name')
    department_id = fields.Many2one('department', string='Department')
    max_cred_require = fields.Integer('Max Credits Requires')
    total_cred = fields.Integer('Total Credits', compute='get_total_cred',
                                help='Course with P/F option will not be counted toward total Credits.')
    # Get P/F course credits
    total_cred_not_count = fields.Integer('Total P/F Credits', compute='get_total_cred',
                                          help='Total credits for P/F Courses')
    max_course_require = fields.Integer('Max Courses Requires')
    is_eng_req = fields.Boolean('Intensive English')
    note = fields.Text('Note')
    
    # List of course
    course_ids = fields.Many2many('course', string='Course List')
    
    # If PE courses needed to fix for Credit count, FIX HERE
    
    #
    @api.depends('course_ids')
    def get_total_cred(self):
        for record in self:
            if record.course_ids:
                total = 0
                total_no_count = 0
                for course in record.course_ids:
                    if course.cred_count_type == 'count':
                        total += course.number_credits
                    elif course.cred_count_type == 'nocount':
                        total_no_count += course.number_credits
                record.total_cred = total
                record.total_cred_not_count = total_no_count
