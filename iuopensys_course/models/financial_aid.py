from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError, Warning

class FinancialAid(models.Model):
    
    _name = 'financial.aid'
    _description = 'Student Financing Options'
    
    name = fields.Char('Name')
    description = fields.Text('Description')
    note = fields.Text('Note')
    finance_type = fields.Selection(selection=[('percent', 'Percentage'),
                                               ('amount', 'Amount')])
    finance_value = fields.Float('Value')
    is_active = fields.Boolean('Active')
    
    # Financial Valid range
    start_date = fields.Date(string='Valid from')
    end_date = fields.Date(string='Until to')
    
    payment_type = fields.Selection(selection=[('deduct','Deduct from Tuition'),
                                               ('paystudent','Pay to Student')],
                                    string='Payment Type',
                                    default='deduct')
    
    # List of student with same Financial Aid Type
    student_ids = fields.One2many('student.financial.aid','financial_aid_id', string='Students')
    
    @api.constrains('start_date', 'end_date')
    def check_start_end_time(self):
        for record in self:
            start = datetime.strptime(record.start_date,"%Y-%m-%d")
            end = datetime.strptime(record.end_date,"%Y-%m-%d")
            diff = int((end-start).days)
            if diff < 0:
                raise ValidationError('End Date must be larger than Start Date')
            if datetime.now() < start or datetime.now() > end:
                if record.is_active:
                    raise ValidationError('Out of valid period for activation.')
        
    @api.multi
    def toggle_active_opt(self):
        for record in self:
            start = datetime.strptime(record.start_date,"%Y-%m-%d")
            end = datetime.strptime(record.end_date,"%Y-%m-%d")
            
            record.is_active = not record.is_active
            
#             if record.is_active:
#                 if datetime.now() < start or datetime.now() > end:
#                     raise Warning('Out of valid period for activation.')