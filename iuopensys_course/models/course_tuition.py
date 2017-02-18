from openerp import models, fields, api

class CourseTuition(models.Model):
    
    _name = 'course.tuition'
    _decription = 'Course Tuition'
    
    name = fields.Char('Name')
    currency = fields.Selection(selection=[('usd', 'US Dollars (USD)'),
                                           ('vnd', 'Vietnam Dong (VND)')],
                                string='Currency')
    usd_to_vnd_rate = fields.Float(string='USD to VND rate (x1000)')
    vnd_to_usd_rate = fields.Float(string='VND to USD rate (with 1000 VND)')
    credit_cost = fields.Float(string='Credit cost',
                               help='Cost for a course\'s credit')
    
    
    