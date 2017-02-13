from openerp import models, fields, api


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    wage_incr_count = fields.Integer(string='Payroll Wage History',
                                     compute='_compute_incr_count')

    @api.multi
    def _compute_incr_count(self):
        for x in self:
            tpw_history = self.env['trobz.payroll.wage.history']
            x.wage_incr_count = tpw_history.search_count(
                [('employee_id', '=', x.id),
                 ('difference', '>', 0)])
