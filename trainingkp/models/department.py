from openerp import models, api, fields


class Department(models.Model):

    _name = 'department'
    _description = 'Department'

    name = fields.Char('Department Name', required=True)
    head_dept_id = fields.Many2one('lecturer', required=True)
    dept_office_numb = fields.Char('Office Number', required=True)
