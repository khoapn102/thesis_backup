# -*- coding: utf-8 -*-

from openerp import models, api, fields

class Major(models.Model):
    
    _name = 'major'
    _description = 'Major'
    
    name = fields.Char(string='Major Name', required=True)
    department_id = fields.Many2one('department', string='Department',
                              required=True)
    major_code = fields.Char(string='Major Code', required=True)
    certified_name = fields.Char(string='Name on Certification', required=True,
                                 help='Name that will appeared on certification')
    
    