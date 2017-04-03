# -*- coding: utf-8 -*-

from openerp import models, api, fields

class Major(models.Model):
    
    _name = 'major'
    _description = 'Major'
    
    name = fields.Char(string='Major Name', required=True)
    department_id = fields.Many2one('department', string='Department')
    major_code = fields.Char(string='Major Code')
    certified_name = fields.Char(string='Name on Certification',
                                 help='Name that will appeared on certification')
    note = fields.Text('Note')

    