from openerp import models, fields, api
from datetime import datetime

class YearBatch(models.Model):
    
    _name = 'year.batch'
    _description = 'Year Batch'
    
    name = fields.Char(string='Name', compute='_generate_name')
    year = fields.Char(string='Intake Year', default=str(datetime.now().year), required=True)
    school_year = fields.Char(string='School Year')
    year_code = fields.Char(string='Student Year Code', compute='_generate_year_code')
    academic_year_ids = fields.One2many('academic.year','year_batch_id', string='Academic Years')
    program_year = fields.Char(string='Program Year (Est.)')

    _sql_constraints = [('year_unique','unique(year)','There is existing Year Batch !')]
    
    @api.onchange('year')
    def onchange_year(self):
        if self.year:
            self.school_year = self.year + '-' + str(int(self.year) + 1)
            self.program_year = self.year + '-' + str(int(self.year) + 4)
    
    @api.multi
    def _generate_name(self):
        for record in self:
            record.name = 'Year ' + (record.year or "") + '-' + (str(int(record.year)+1) or "")           
    
    @api.multi
    def _generate_year_code(self):
        for record in self:
            record.year_code = 'K' + (str(int(record.year) % 100) or "")
            
            