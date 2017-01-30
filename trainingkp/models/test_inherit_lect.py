from openerp import models, fields, api


class TestInheritLect(models.Model):

    _name = 'lecturer'
    _inherit = 'lecturer'
    _description = 'Test Inherit Lecturer'

    hobby = fields.Char(string='Hobbies')
    contract_type = fields.Selection(string='Contract Type',
                                     selection=[('perm', 'Permanent'),
                                                ('temp', 'Temporary')])

    contract_duration = fields.Selection(string='Contract Duration',
                                         selection=[('six', 'Six Months'),
                                                    ('ayr', 'A Year'),
                                                    ('thryr', 'Three Years')])

    is_signed = fields.Boolean(string='Contract Signed?')
