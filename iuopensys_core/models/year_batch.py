from openerp import models, fields, api
from datetime import datetime

class YearBatch(models.Model):
    
    _name = 'year.batch'
    _description = 'Year Batch'
    
    name = fields.Char(string='Year Batch', compute='_generate_name')
    year = fields.Char(string='Year', default=str(datetime.now().year), required=True)
    year_code = fields.Char(string='Year Code', compute='_generate_year_code')
    academic_year_ids = fields.One2many('academic.year','year_batch_id', string='Academic Years')

    _sql_constraints = [('year_unique','unique(year)','There is existing Year Batch !')]
    
    @api.multi
    def _generate_name(self):
        for record in self:
            record.name = 'Batch ' + (record.year or "")            
    
    @api.multi
    def _generate_year_code(self):
        for record in self:
            record.year_code = 'K' + (str(int(record.year) % 100) or "")
            
            