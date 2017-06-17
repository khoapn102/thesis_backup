from openerp import models, fields, api

class StudentFinancialAid(models.Model):
    
    _name = 'student.financial.aid'
    _description = 'Manage student and financial aid'
    
    # Student
    student_id = fields.Many2one('student', string='Student')
    studentId = fields.Char(string='Student ID', related='student_id.studentId')
    student_lname = fields.Char(string='Last Name', related='student_id.last_name')
    student_fname = fields.Char(string='First Name', related='student_id.name')
    student_class_code = fields.Char(string='Student Class Code', related='student_id.student_class_code')
    student_dob = fields.Date(related='student_id.birthdate')
    student_dept_id = fields.Many2one(related='student_id.department_id')
    student_major_id = fields.Many2one(related='student_id.major_id')
    student_academic_yr_id = fields.Many2one(related='student_id.academic_year_id')
    student_country = fields.Many2one(related='student_id.country_id')
    
    financial_aid_id = fields.Many2one('financial.aid', string='Financial Aid')
    
    start_date = fields.Date(related='financial_aid_id.start_date')
    end_date = fields.Date(related='financial_aid_id.end_date')
    finance_type = fields.Selection(related='financial_aid_id.finance_type')
    finance_value = fields.Float(related='financial_aid_id.finance_value')
    
    is_active = fields.Boolean('Active')
    
    @api.multi
    def set_is_active(self):
        for record in self:
            record.is_active = not record.is_active
            
    @api.multi
    def unlink(self):
        for record in self:
            if record.student_id.financial_aid_id.id == record.financial_aid_id.id:
                student = self.env['student'].search([('id','=',record.student_id.id)])
                student.write({'financial_aid_id':False})
        return models.Model.unlink(self)
    