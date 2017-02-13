from openerp import models, fields, api


class Lecturer(models.Model):

    _name = 'lecturer'
    _description = 'Lecturer'

    name = fields.Char(string='Lecturer Name', required=True)
    lecturerId = fields.Char(string='Lecturer ID', required=True)
    id_number = fields.Char(string='Identify Number', required=True)
    gender = fields.Selection(
        selection=[('m', 'Male'), ('f', 'Female')], string='Gender')
    image = fields.Binary()
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    address = fields.Text(string='Address', required=True)
    phone = fields.Char(string='Phone Number')
    department_id = fields.Many2one(
        'department', string='Department')
    head_dept_id = fields.Many2one(
        'lecturer', related='department_id.head_dept_id', string='Head Dept ID')
