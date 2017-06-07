from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError

class Semester(models.Model):
    
    _name = 'semester'
    _description = 'Semester'
    _order = 'semester_year, semester_type, id'
    
    name = fields.Char(string='Semester', compute='_get_semester_name')
    semester_year = fields.Char(string='Year',required=True,
                       default=(str(datetime.now().year) + '-' + str(datetime.now().year + 1)))
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
    checkfield = fields.Char(string='Unique Field', default='Test')
    
    _sql_constraints = [('checkfield_unique', 'unique(checkfield)', 'There is existing Semester')]
    
    @api.onchange('semester_type','semester_year')
    def _onchange_semester_type(self):
        self.checkfield = self.semester_year + (self.semester_type or "")
        
    @api.multi
    def _get_semester_name(self):
        for record in self:
            record.name = record.semester_type + '-' + record.semester_year.split('-')[0]
    @api.multi
    def _get_semester_code(self):
        for record in self:
            record.semester_code = record.semester_year.split('-')[0] + (record.semester_type or "")
    
    @api.onchange('start_date')
    def _onchange_start_date(self):
        self.end_date = (datetime.strptime(self.start_date,'%Y-%m-%d') +\
                        relativedelta(days=112)).strftime('%Y-%m-%d')
    
    @api.constrains('start_date', 'end_date')
    def _validate_academic_year_period(self):
        for record in self:
            start = datetime.strptime(record.start_date,"%Y-%m-%d")
            end = datetime.strptime(record.end_date,"%Y-%m-%d")
            diff = int((end-start).days)
            if diff < 0:
                raise ValidationError('End Date must be larger than Start Date')
            