from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError

class Semester(models.Model):
    
    _name = 'semester'
    _description = 'Semester'
    
    name = fields.Char(string='Semester')
    semester_year = fields.Char(string='Year',required=True,
                       default=str(datetime.now().year))
    semester_type = fields.Selection(selection=[('1', 'Semester 1'),
                                                ('2', 'Semester 2'),
                                                ('3', 'Semester 3')],
                                     string='Semester Type', required=True)
    semester_code = fields.Char(string='Semester Code',
                                compute='_get_semester_code')
    start_date = fields.Date(string='Starting Date', required=True,
                             default=datetime.now().strftime("%Y-%m-%d"))
    end_date = fields.Date(string='Ending Date', required=True,
                           default=datetime.now() + relativedelta(days=112))
    
    @api.multi
    def _get_semester_code(self):
        for record in self:
            record.semester_code = record.semester_year + (record.semester_type or "")
    
    @api.constrains('start_date', 'end_date')
    def _validate_academic_year_period(self):
        for record in self:
            start = datetime.strptime(record.start_date,"%Y-%m-%d")
            end = datetime.strptime(record.end_date,"%Y-%m-%d")
            diff = int((end-start).days)
            if diff < 0:
                raise ValidationError('End Date must be larger than Start Date')
            