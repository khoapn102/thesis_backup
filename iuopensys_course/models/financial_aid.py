from openerp import models, fields, api

class FinancialAid(models.Model):
    
    _name = 'financial.aid'
    _description = 'Student Financing Options'
    
    name = fields.Char('Name')
    description = fields.Text('Description')
    note = fields.Text('Note')
    finance_type = fields.Selection(selection=[('percent', 'Percentage'),
                                               ()])