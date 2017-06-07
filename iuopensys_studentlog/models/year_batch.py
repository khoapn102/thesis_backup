from openerp import models, fields, api

class YearBatch(models.Model):
    
        
    _inherit='year.batch'
    
    student_ids = fields.One2many('student', 'year_batch_id', string='Students')
    
    graduating_student_ids = fields.Many2many('student',string='Graduating Students',
                                              help='Students who are ready to graduate this year.',
                                              compute='get_graduating_student_ids')
    
    @api.depends('student_ids')
    def get_graduating_student_ids(self):
        for record in self:
            res_ids = self.env['student'].search([('graduation_status','=','complete'),
                                                    ])
            print '=====', res_ids
            record.graduating_student_ids = res_ids