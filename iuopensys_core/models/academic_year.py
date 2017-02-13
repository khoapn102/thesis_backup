from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class AcademicYear(models.Model):
    
    """
        Academic Year (Class of Student)
    """
    
    _name = 'academic.year'
    _description = 'Academic Year - Class of Student'
    
    name = fields.Char(string='Academic Year', size=128, required=True)
    year_batch_id = fields.Many2one('year.batch', string='Year Batch', size=10, required=True,
                                    ondelete="cascade")
    lecturer_id = fields.Many2one('lecturer', string='Academic Advisor', 
                                  required=True,
                                  domain="[('department_id','=',department_id)]")
    class_code = fields.Char(string='Class Code', compute='_get_class_code')
    department_id = fields.Many2one('department', string='Department', required=True)
    start_date = fields.Date(string='Starting Date', required=True,
                             default=datetime.now().strftime("%Y-%m-%d"))
    end_date = fields.Date(string='Ending Date', required=True,
                           default=datetime.now() + relativedelta(years=4))

    @api.onchange('department_id','year_batch_id')
    def _produce_name(self):
        if self.department_id.id and self.year_batch_id:
            self.name = self.department_id.dept_academic_code + '-'+ (self.year_batch_id.year or "")
    
    @api.multi
    def _get_class_code(self):
        for record in self:
            dept_academic_code = record.department_id.dept_academic_code
            record.class_code = dept_academic_code*2 +\
                                 str(int(record.year_batch_id.year or 0)%100)
    
    @api.constrains('start_date', 'end_date')
    def _validate_academic_year_period(self):
        for record in self:
            start = datetime.strptime(record.start_date,"%Y-%m-%d")
            end = datetime.strptime(record.end_date,"%Y-%m-%d")
            diff = int((end-start).days)
            if diff < 0:
                raise ValidationError('End Date must be larger than Start Date')
            
    @api.model
    def create(self, vals):
        curr_year = super(AcademicYear,self).create(vals)
        dept_code = 'student.'
        dept_code += str(curr_year.department_id.dept_academic_code).lower()
        seq_id = self.env['ir.sequence'].search([('code','=',dept_code)])
        if seq_id:
            seq_id.write({'number_next_actual': 1,})
        return curr_year
    