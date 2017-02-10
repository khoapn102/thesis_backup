from openerp import models, fields, api

class PartB(models.Model):
    
    _name = 'part.b'
    _description = 'Test B'
    
    name = fields.Char('Name')
    part_a_id = fields.Many2one('part.a','Part A')