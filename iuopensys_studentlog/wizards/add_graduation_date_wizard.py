from openerp import models, fields, api

class AddGraduationDateWizard(models.TransientModel):
    
    _name = 'add.graduation.date.wizard'
    _description = 'Set Graduation Date for Student'
    
    name = fields.Char(string='Name')
    student_id = fields.Many2one('student', string='Student')
    graduation_date = fields.Date(string='Graduated on')
    
    @api.multi
    def add_graduation_date(self):
        for record in self:
            if record.student_id and record.graduation_date:
                new_vals = {'graduation_date': record.graduation_date,
                            'graduation_status': 'graduated'}
                student = self.env['student'].search([('id','=',record.student_id.id)])
                student.write(new_vals)