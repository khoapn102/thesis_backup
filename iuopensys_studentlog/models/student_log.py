from openerp import models, fields, api

class StudentLog(models.Model):
    
    _name = 'student.log'
    _description = 'Student Log'
    
    name = fields.Char('Name', default='Data')
    student_id = fields.Many2one('student', string='Student')
    modified_user_id = fields.Many2one('res.users', string='Modified by')
    field_change = fields.Char('Field Changed')
    field_change_name = fields.Char('Field\'s name')
    old_value = fields.Text('Old Data')
    new_value = fields.Text('New Data')
    modified_date = fields.Datetime('Modified Date & Time')
    