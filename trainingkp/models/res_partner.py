from openerp import models, fields, api


class ResPartner(models.Model):

    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Resource Partner'

    contract_type = fields.Selection(string='Contract Type',
                                     selection=[('consgn', 'Consignment'),
                                                ('orgt', 'Outright')])
